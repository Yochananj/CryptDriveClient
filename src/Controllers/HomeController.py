import json
import logging
import os.path

import flet as ft


from Dependencies.Constants import crypt_drive_blue, crypt_drive_theme, crypt_drive_fonts
from Dependencies.VerbDictionary import Verbs
from Services.ClientFileService import ClientFileService
from Views.AccountContainer import AccountContainer
from Views.FileContainer import FileContainer
from Views.HomeView import HomeView
from Views.SettingsContainer import SettingsContainer
from Views.UIElements import error_alert, FolderTile, FileTile, success_alert
from Views.ViewsAndRoutesList import ViewsAndRoutesList


class HomeController:
    def __init__(self, page: ft.Page, view: HomeView, navigator, comms_manager, client_file_service: ClientFileService):
        self.view: HomeView = view
        self.navigator = navigator
        self.comms_manager = comms_manager
        self.page = page
        self.page.theme = crypt_drive_theme
        self.container = None
        self.current_dir = "/"
        self.client_file_service: ClientFileService = client_file_service

        self.page.fonts = crypt_drive_fonts

        self.page.views[0].floating_action_button_location = ft.FloatingActionButtonLocation.START_FLOAT
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.file_container = FileContainer(self.page)
        self.account_container = AccountContainer()
        self.settings_container = SettingsContainer()

        self.mini_navigator()
        self.attach_handlers()


    def attach_handlers(self):
        self.view.nav_rail.on_change = self.mini_navigator
        self.attach_handlers_per_destination()
        self.page.on_resized = lambda e: self.on_resize()

    def on_resize(self):
        self.view.nav_rail.height = self.page.height
        self.view.body.height = self.page.height
        self.view.body.width = self.page.width

        match self.view.nav_rail.selected_index:
            case 0:
                self.container.animator.height = self.page.height - 90
                self.container.animator.width = self.page.width - 100
            case 1:
                pass
            case 2:
                pass

        self.page.update()

    def mini_navigator(self, control_event=None):
        logging.debug(f"switched to destination: {self.view.nav_rail.selected_index}")
        logging.debug(control_event)

        match self.view.nav_rail.selected_index:
            case 0:  # Files container
                self.page.title = "CryptDrive: Files"
                self.container: FileContainer = self.file_container

                self.container.column.controls = []
                self.container.tiles.controls = []
                self.container.column.controls.append(self.container.title)
                self.container.column.controls.append(self.container.animator)

                self.view.body.content = self.container.build()
                self.page.update()

                self.container.animator.content = self.container.loading
                self.container.animator.update()

                self.container.animator.content = self.container.tiles

                self.container.current_directory = FolderTile(path=self.current_dir, item_count=None, is_current_directory=True,)

                self.container.subtitle_row.controls = []
                self.container.subtitle_row.controls.append(self.container.current_directory.tile)
                self.container.subtitle_row.controls.append(self.container.upload_file_button)
                self.container.subtitle_row.controls.append(self.container.create_dir_button)


                self.container.tiles.controls.append(self.container.subtitle_row)

                dir_list, file_list = self.get_file_list()

                self.container.directories, self.container.files = [], []

                for directory in dir_list:
                    self.container.directories.append(
                        FolderTile(
                            path=directory["path"],
                            item_count=directory["item_count"]
                        )
                    )
                for file in file_list:
                    self.container.files.append(
                        FileTile(
                            file_name=file["name"],
                            file_size=file["size"]
                        )
                    )
                for directory in self.container.directories:
                    self.container.tiles.controls.append(directory.tile)
                for file in self.container.files:
                    self.container.tiles.controls.append(file.tile)
                self.container.animator.content = self.container.tiles


            case 1:  # Account container
                self.page.title = "CryptDrive: Account"
                self.container: AccountContainer = self.account_container

            case 2:  # Settings container
                self.page.title = "CryptDrive: Settings"
                self.container: SettingsContainer = self.settings_container

        self.view.body.content = self.container.build()
        self.container.title.font_family = "Aeonik Black"
        self.container.title.size = 90
        self.container.title.color = crypt_drive_blue
        self.container.column.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

        self.attach_handlers_per_destination()

        self.page.update()

    def attach_handlers_per_destination(self):
        match self.view.nav_rail.selected_index:
            case 0:  # Files container
                self.container.animator.update()

                # Current Dir FolderTile
                parent_dir = self.container.current_directory.path[:-1] if self.container.current_directory.path[:-1] != "" else "/"
                if self.container.current_directory.path + self.container.current_directory.name != "/":
                    self.container.current_directory.tile.on_click = lambda e: self.change_dir(parent_dir)

                # `Upload File` button
                self.container.upload_file_button.on_click = lambda e: self.upload_file_button_on_click()

                # `Create Directory` button and dialog
                self.container.create_dir_button.on_click = lambda e: self.page.open(self.container.create_dir_dialog)
                self.container.create_dir_dialog_confirm.on_click = lambda e, dir_name_text_field=self.container.create_dir_dialog_text_field: self.create_dir_confirm_on_click(dir_name_text_field.value)
                self.container.create_dir_dialog_cancel.on_click = lambda e: self.page.close(self.container.create_dir_dialog)

                # FolderTiles
                for directory in self.container.directories:
                    directory.tile.on_click = lambda e, dp = directory.path, dn = directory.name: self.change_dir(dp + dn)
                    directory.delete.on_click = lambda e, d = directory: self.delete_dir_on_click(d)

                # FileTile Download Buttons
                for file in self.container.files:
                    file.download.on_click = lambda e, fn=file.name: self.download_file_on_click(fn)


            case 1:  # Account container
                self.account_container.log_out_button.on_click = lambda e: self.log_out()

            case 2:  # Settings container
                pass

    def change_dir(self, path):
        self.current_dir = path
        self.mini_navigator()

    def upload_file_button_on_click(self):
        file = self.client_file_service.file_picker()
        if file is None or file == "": return
        else: file = str(file)

        logging.debug(f"Uploading file: {file}")
        file_name = os.path.basename(file)
        file_contents = self.client_file_service.read_file_from_disk(file)
        status, response = self.comms_manager.send_message(Verbs.CREATE_FILE, [self.current_dir, file_name, file_contents])
        if status == "SUCCESS":
            logging.debug("File uploaded successfully")
            self.mini_navigator()
            self.page.open(success_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} uploaded successfully"))
        else:
            logging.debug("File upload failed")
            self.page.open(error_alert("File Upload Failed. Please Try Again"))

    def create_dir_confirm_on_click(self, dir_name: str):
        if len(dir_name) == 0:
            self.page.open(error_alert("Directory Name Cannot Be Empty"))
            return

        if not dir_name.isalnum():
            self.page.open(error_alert("Directory Name Cannot Contain symbols'"))
            return

        self.page.close(self.container.create_dir_dialog)
        logging.debug(f"Current dir: {self.current_dir}")
        logging.debug(f"Dir name: {dir_name}")
        data = [self.current_dir, dir_name]
        status, response = self.comms_manager.send_message(verb=Verbs.CREATE_DIR, data=data)
        if status == "SUCCESS":
            logging.debug("Directory created successfully")
            self.mini_navigator()
            self.page.open(success_alert(f"Directory {self.current_dir if self.current_dir != "/" else ""}/{dir_name} created successfully"))
        else:
            logging.debug("Directory creation failed")
            self.mini_navigator()
            self.page.open(error_alert("Directory name already taken. Please try again with a different name."))
        self.container.create_dir_dialog_text_field.value = ""

    def delete_dir_on_click(self, directory: FolderTile):
        self.container.delete_file_dialog_title.value = f"Are you sure you want to delete \"{directory.name}\"?"
        self.page.open(self.container.delete_file_dialog)
        self.container.delete_file_dialog_confirm.on_click = lambda e, d=directory: self.delete_dir(d.path, d.name)
        self.container.delete_file_dialog_cancel.on_click = lambda e: self.page.close(self.container.delete_file_dialog)

    def delete_dir(self, dir_path, dir_name):
        self.page.close(self.container.delete_file_dialog)
        logging.debug(f"Deleting directory: [{dir_path}, {dir_name}]")
        status, response = self.comms_manager.send_message(verb=Verbs.DELETE_DIR, data=[dir_path, dir_name])
        if status == "SUCCESS":
            logging.debug(f"Directory [{dir_path}, {dir_name}] deleted successfully")
            self.mini_navigator()
            self.page.open(success_alert(f"Directory {dir_path if dir_path != "/" else ""}/{dir_name} deleted successfully"))
        else:
            logging.debug("Directory deletion failed")
            self.page.open(error_alert(f"Directory {dir_path if dir_path != "/" else ""}/{dir_name} Deletion Failed. Please Try Again"))

    def download_file_on_click(self, file_name):
        data = [self.current_dir, file_name]
        status, file_bytes = self.comms_manager.send_message(verb=Verbs.DOWNLOAD_FILE, data=data)
        if status == "SUCCESS":
            logging.debug("Download successful \n Writing to file")
            path_to_save_to = self.client_file_service.dir_picker()
            logging.debug(f"Path to save to: {path_to_save_to if path_to_save_to is not None or "" else 'Empty'}")
            if path_to_save_to is None or path_to_save_to == "": return
            self.client_file_service.save_file_to_disk(path_to_save_to, file_name, file_bytes)
            logging.debug("File saved successfully")
        else:
            logging.debug("Download failed")
            self.page.open(error_alert("Download Failed. Please Try Again"))

    def get_file_list(self):
        logging.debug("Getting file list")
        status, dirs_and_files = self.comms_manager.send_message(verb=Verbs.GET_ITEMS_LIST, data=[self.current_dir])

        logging.debug(f"status: {status}")
        logging.debug(f"dirs_and_files: <{dirs_and_files}>, type: {type(dirs_and_files)}")
        logging.debug(f"dirs_and_files[0]: {dirs_and_files[0]}")

        dirs, files = json.loads(json.loads(dirs_and_files)["dirs_dumps"]), json.loads(json.loads(dirs_and_files)["files_dumps"])

        return dirs, files

    def log_out(self):
        self.comms_manager.token = 'no_token'
        self.navigator(ViewsAndRoutesList.LOG_IN)



