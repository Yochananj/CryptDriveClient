import json
import logging
import os.path
import time
from base64 import b64decode

import flet as ft

from Dependencies.Constants import crypt_drive_theme, crypt_drive_fonts
from Dependencies.VerbDictionary import Verbs
from Services.ClientCommsManager import ClientCommsManager
from Services.ClientFileService import ClientFileService
from Services.FileEncryptionService import FileEncryptionService
from Services.PasswordsService import PasswordsService
from Views.AboutContainer import AboutContainer
from Views.AccountContainer import AccountContainer
from Views.FileContainer import FileContainer
from Views.HomeView import HomeView
from Views.UIElements import error_alert, FolderTile, FileTile, success_alert, TextFieldAlertDialog, \
    CancelConfirmAlertDialog, FolderPickerAlertDialog
from Views.ViewsAndRoutesList import ViewsAndRoutesList


class HomeController:
    def __init__(self, page: ft.Page, view: HomeView, navigator, comms_manager: ClientCommsManager, client_file_service: ClientFileService, file_encryption_service: FileEncryptionService, passwords_service: PasswordsService, username):
        self.view: HomeView = view
        self.navigator = navigator
        self.comms_manager = comms_manager
        self.file_encryption_service = file_encryption_service
        self.passwords_service = passwords_service
        self.username = username

        self.page: ft.Page = page
        self.page.theme = crypt_drive_theme
        self.page.scroll = True
        self.container = None
        self.current_dir = "/"
        self.client_file_service: ClientFileService = client_file_service

        self.selected_container: int = 0

        self.page.fonts = crypt_drive_fonts
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.file_container = FileContainer()
        self.account_container = AccountContainer(username=username)
        self.about_container = AboutContainer()

        self._mini_navigator()
        self._attach_handlers()

    def _attach_handlers(self):
        self.view.nav_rail.on_change = self._mini_navigator
        self._attach_handlers_per_destination()
        self.page.on_resized = lambda e: self._on_resize()
        self.view.nav_rail.destinations[0].on_click = lambda e: self._change_dir("/")

    def _on_resize(self):
        self.view.body.height = self.page.window.height
        self.view.body.width = self.page.window.width - 130

        match self.view.nav_rail.selected_index:
            case 0:
                self.container.animator.height = self.page.window.height - 170
                self.container.animator.width = self.page.window.width - 130
                pass
            case 1:
                pass
            case 2:
                pass

        self.page.update()

    def _mini_navigator(self, control_event=None, force_animation=False):
        logging.debug(f"Switched to destination: {self.view.nav_rail.selected_index}")
        logging.debug(f"Control event: {control_event.__dict__ if control_event else 'None'}")
        self.view.home_view_animator.content = self.view.loading
        self.page.add(self.view.home_view_animator)

        if self.selected_container != self.view.nav_rail.selected_index or force_animation:
            self.view.home_view_animator.update()
            time.sleep(0.3)

        match self.view.nav_rail.selected_index:
            case 0:  # Files container
                self.selected_container = 0

                if control_event:
                    self.current_dir = "/"

                self.page.title = "CryptDrive: Files"
                self.container: FileContainer = self.file_container

                self.container.animator.content = ft.Container()

                self.container.column.controls = [
                    self.container.title,
                    self.container.animator
                ]

                self.view.body.content = self.container.column
                self.view.home_view_animator.content = self.view.body
                self.page.update()
                time.sleep(0.2)

                self.container.current_directory = FolderTile(path=self.current_dir, item_count=None, compact_tile=True)

                self.container.subtitle_row.controls = [
                    self.container.current_directory.tile,
                    self.container.upload_file_button,
                    self.container.create_dir_button
                ]

                self.container.tiles_column.controls = [self.container.subtitle_row]
                self.container.animator.content = self.container.tiles_alignment_container
                self.container.animator.update()

                dir_list, file_list = self._get_file_list(self.current_dir)

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
                    animator = ft.AnimatedSwitcher(
                        ft.Container(),
                        transition=ft.AnimatedSwitcherTransition.FADE,
                        duration=300,
                        reverse_duration=300,
                        switch_in_curve=ft.AnimationCurve.EASE_IN,
                        switch_out_curve=ft.AnimationCurve.EASE_OUT,
                    )
                    self.page.add(animator)
                    self.container.tiles_column.controls.append(animator)
                    self.container.animator.update()

                    time.sleep(0.1)
                    animator.content = directory.tile
                    animator.update()

                for file in self.container.files:
                    animator = ft.AnimatedSwitcher(
                        ft.Container(),
                        transition=ft.AnimatedSwitcherTransition.FADE,
                        duration=300,
                        reverse_duration=300,
                        switch_in_curve=ft.AnimationCurve.EASE_IN,
                        switch_out_curve=ft.AnimationCurve.EASE_OUT,
                    )
                    self.page.add(animator)
                    self.container.tiles_column.controls.append(animator)
                    self.container.animator.update()

                    time.sleep(0.1)
                    animator.content = file.tile
                    animator.update()



            case 1:  # Account container
                self.page.title = "CryptDrive: Account"
                self.container: AccountContainer = self.account_container
                self.view.body.content = self.container.column
                self.view.home_view_animator.content = self.view.body

                if self.selected_container != 1:
                    self.container.animator.content = ft.Container()
                    self.container.column.controls = [self.container.title, self.container.animator]
                    self.page.add(self.container.animator)

                    self.page.update()
                    time.sleep(0.2)

                    self.container.animator.content = ft.Column([self.container.account_details])

                    self.page.update()
                    time.sleep(0.1)

                    row = ft.Row()
                    self.container.animator.content.controls.append(row)
                    for button in self.container.buttons:
                        animator = ft.AnimatedSwitcher(
                            ft.Container(),
                            transition=ft.AnimatedSwitcherTransition.FADE,
                            duration=300,
                            reverse_duration=300,
                            switch_in_curve=ft.AnimationCurve.EASE_IN,
                            switch_out_curve=ft.AnimationCurve.EASE_OUT,
                        )
                        row.controls.append(animator)
                        self.page.update()
                        animator.content=button
                        time.sleep(0.1)

                self.page.update()


                self.selected_container = 1

            case 2:  # Settings container

                self.page.title = "CryptDrive: Settings"
                self.container: AboutContainer = self.about_container

                self.page.add(self.container.animator)

                self.view.body.content = self.container.column
                self.view.home_view_animator.content = self.view.body

                self.page.update()

                if self.selected_container != 2:
                    self.container.animator.content.controls = []

                    for line in self.container.about_lines:
                        animator = ft.AnimatedSwitcher(
                            ft.Container(),
                            transition=ft.AnimatedSwitcherTransition.FADE,
                            duration=300,
                            reverse_duration=300,
                            switch_in_curve=ft.AnimationCurve.EASE_IN,
                            switch_out_curve=ft.AnimationCurve.EASE_OUT,
                        )
                        self.page.add(animator)
                        self.container.animator.content.controls.append(animator)
                        self.container.animator.update()
                        time.sleep(0.1)
                        animator.content = line
                        animator.update()

                    self.selected_container = 2

                self.page.update()

        self.view.home_view_animator.content = self.view.body
        self.view.home_view_animator.update()

        self._attach_handlers_per_destination()
        self.page.update()

    def _attach_handlers_per_destination(self):
        match self.view.nav_rail.selected_index:
            case 0:  # Files container

                # Current Dir FolderTile
                if self.container.current_directory.path + self.container.current_directory.name != "/":
                    self.container.current_directory.tile.on_click = lambda e: self._change_dir("/" if self.container.current_directory.path == "/" else self.container.current_directory.path[:-1])

                # `Upload File` button
                self.container.upload_file_button.on_click = lambda e: self._upload_file_button_on_click()

                # `Create Directory` button and dialog
                self.container.create_dir_button.on_click = lambda e: self._create_dir_button_on_click()

                # FolderTiles
                for directory in self.container.directories:
                    directory.tile.on_click = lambda e, dp = directory.path, dn = directory.name: self._change_dir(dp + dn)
                    directory.delete.on_click = lambda e, d = directory: self._delete_dir_on_click(d)
                    directory.rename.on_click = lambda e, d = directory: self._rename_dir_on_click(d.name)
                    directory.move.on_click = lambda e, dn = directory.name: self._move_dir_on_click(dn)

                # FileTile Download Buttons
                for file in self.container.files:
                    file.download.on_click = lambda e, fn=file.name: self._download_file_on_click(fn)
                    file.delete.on_click = lambda e, fn=file.name: self._delete_file_on_click(fn)
                    file.rename.on_click = lambda e, fn=file.name: self._rename_file_on_click(fn)
                    file.move.on_click = lambda e, fn=file.name: self._move_file_on_click(fn)


            case 1:  # Account container
                self.account_container.change_username_button.on_click = lambda e: self._change_username_on_click()
                self.account_container.change_password_button.on_click = lambda e: self._change_password_on_click()
                self.account_container.log_out_button.on_click = lambda e: self._log_out()

            case 2:  # About container
                pass

    def _change_dir(self, path):
        self.current_dir = path
        self._mini_navigator()

    def _upload_file_button_on_click(self):
        self.page.window.to_front()
        file = self.client_file_service.file_picker_dialog()
        if file is None or file == "": return
        else: file = str(file)

        logging.debug(f"Uploading file: {file}")
        file_name = os.path.basename(file)
        file_contents = self.client_file_service.read_file_from_disk(file)

        encrypted_file_contents, file_nonce = self.file_encryption_service.encrypt_file(file_contents)

        status, response = self.comms_manager.send_message(Verbs.CREATE_FILE, [self.current_dir, file_name, file_nonce, encrypted_file_contents])
        if status == "SUCCESS":
            logging.debug("File uploaded successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} uploaded successfully"))
        else:
            logging.debug("File upload failed")
            self.page.open(error_alert(f"File Upload Failed. Please Try Again. (Error Code: {response})"))

    def _rename_file_on_click(self, old_file_name):
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Rename File:",
            title_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED,
            subtitle=f"Enter the new file name for the file '{old_file_name}':",
            text_fields=["New File Name:"],
            modal=False
        )
        dialog.set_on_confirm_method(lambda e: self._rename_file(old_file_name, dialog=dialog))
        self.page.open(dialog.alert)

    def _rename_file(self, old_file_name, dialog, file_extension_change_dialog=None, override_file_extension: bool = False):
        new_file_name = dialog.get_text_field_values()[0]
        logging.debug(f"Current dir: {self.current_dir}")
        logging.debug(f"Old file name: {old_file_name}")
        logging.debug(f"New file name: {new_file_name}")
        self.page.close(dialog.alert)

        if len(new_file_name) == 0:
            self.page.open(error_alert("File Name cannot be empty. Please try again with a different name."))
            return

        if "/" in new_file_name:
            self.page.open(error_alert("File Name cannot contain slashes. Please try again with a different name."))
            return

        if "|" in new_file_name:
            self.page.open(error_alert("File Name cannot contain pipes. Please try again with a different name."))
            return

        if "." in old_file_name and (new_file_name.split(".")[-1] != old_file_name.split(".")[-1] or not new_file_name) and not override_file_extension:
            confirmation_dialog = CancelConfirmAlertDialog(
                page=self.page,
                title="Confirm File Extension Change",
                title_icon=ft.Icons.WARNING_ROUNDED,
                subtitle=f"The new file name you have entered (`{new_file_name}`) contains a different file extension than the current file name (`{old_file_name}`).\nAre you sure you want to proceed?"
            )
            confirmation_dialog.set_on_confirm_method(lambda e: self._rename_file(old_file_name, dialog, file_extension_change_dialog=confirmation_dialog, override_file_extension=True))
            self.page.open(confirmation_dialog.alert)
            return

        if override_file_extension:
            self.page.close(file_extension_change_dialog.alert)

        if old_file_name == new_file_name:
            return

        else:
            data = [self.current_dir, old_file_name, new_file_name]
            status, response = self.comms_manager.send_message(verb=Verbs.RENAME_FILE, data=data)
            if status == "SUCCESS":
                logging.debug("File renamed successfully")
                self._mini_navigator()
                self.page.open(success_alert(f"File {old_file_name} renamed successfully to {new_file_name}"))
            else:
                logging.debug("File renaming failed")
                self.page.open(error_alert(f"File renaming failed. Please Try Again. (Error Code: {response})"))

    def _rename_dir_on_click(self, old_dir_name):
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Rename Dir:",
            title_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED,
            subtitle=f"Enter the new file name for the file '{old_dir_name}':",
            text_fields=["New File Name:"],
            modal=False
        )
        dialog.set_on_confirm_method(lambda e: self._rename_dir(old_dir_name, dialog=dialog))
        self.page.open(dialog.alert)

    def _rename_dir(self, old_dir_name, dialog):
        self.page.close(dialog.alert)
        new_dir_name = dialog.get_text_field_values()[0]

        if len(new_dir_name) == 0:
            self.page.open(error_alert("Directory Name cannot be empty. Please try again with a different name."))
            return

        is_name_invalid = False
        for sect in new_dir_name.split(" "):
            if not sect.isalnum() :
                is_name_invalid = True

        if is_name_invalid:
            self.page.open(error_alert("Directory Name cannot contain special characters. Please try again with a different name."))
            return

        data = [self.current_dir, old_dir_name, new_dir_name]
        status, response = self.comms_manager.send_message(verb=Verbs.RENAME_DIR, data=data)
        if status == "SUCCESS":
            logging.debug("Directory renamed successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"Directory {self.current_dir if self.current_dir != "/" else ""}/{old_dir_name} renamed successfully to {self.current_dir if self.current_dir != "/" else ""}/{new_dir_name}"))
        else:
            logging.debug("Directory renaming failed")
            self.page.open(error_alert(f"Directory renaming failed. Please Try Again. (Error Code: {response}"))

    def _create_dir_button_on_click(self):
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Create New Directory:",
            title_icon=ft.Icons.CREATE_NEW_FOLDER_ROUNDED,
            subtitle="Enter the name of the new directory:",
            text_fields=["Directory Name:"],
            modal=False
        )
        dialog.set_on_confirm_method(lambda e: self._create_dir_confirm_on_click(dialog))
        self.page.open(dialog.alert)

    def _create_dir_confirm_on_click(self, dialog):
        dir_name = dialog.get_text_field_values()[0]
        self.page.close(dialog.alert)

        logging.debug(f"Current dir: {self.current_dir}")
        logging.debug(f"Dir name: {dir_name}")

        if len(dir_name) == 0:
            self.page.open(error_alert("Directory Name cannot be empty. Please try again with a different name."))
            return

        is_name_invalid = False
        for sect in dir_name.split(" "):
            if not sect.isalnum():
                is_name_invalid = True

        if is_name_invalid:
            self.page.open(error_alert("Directory Name cannot contain special characters. Please try again with a different name."))
            return


        data = [self.current_dir, dir_name]
        status, response = self.comms_manager.send_message(verb=Verbs.CREATE_DIR, data=data)
        if status == "SUCCESS":
            logging.debug("Directory created successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"Directory {self.current_dir if self.current_dir != "/" else ""}/{dir_name} created successfully"))
        else:
            logging.debug("Directory creation failed")
            self._mini_navigator()
            self.page.open(error_alert(f"Directory name already taken. Please try again with a different name. (Error Code: {response})"))

    def _delete_file_on_click(self, file_name):
        dialog = CancelConfirmAlertDialog(
            page=self.page,
            title="Confirm File Deletion",
            title_icon=ft.Icons.DELETE_ROUNDED,
            subtitle=f"Are you sure you want to delete the file `{file_name}`?",
            modal=False
        )
        dialog.set_on_confirm_method(lambda e, fn=file_name, d=dialog: self._delete_file(fn, d))
        self.page.open(dialog.alert)

    def _delete_file(self, file_name: str, dialog: CancelConfirmAlertDialog):
        self.page.close(dialog.alert)
        logging.debug(f"Deleting file: {self.current_dir if self.current_dir != "/" else ""}/{file_name}")
        status, response = self.comms_manager.send_message(verb=Verbs.DELETE_FILE, data=[self.current_dir, file_name])
        if status == "SUCCESS":
            logging.debug(f"File [{self.current_dir}, {file_name}] deleted successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} deleted successfully"))
        else:
            logging.debug("File deletion failed")
            self.page.open(error_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} Deletion Failed. Please Try Again"))

    def _delete_dir_on_click(self, directory: FolderTile):
        dialog = CancelConfirmAlertDialog(
            page=self.page,
            title="Confirm Directory Deletion",
            title_icon=ft.Icons.DELETE_ROUNDED,
            subtitle=f"Are you sure you want to delete the directory `{directory.name}`?",
            modal=False
        )
        dialog.set_on_confirm_method(lambda e, dp = directory.path, dn = directory.name: self._delete_dir(dp[:-1] if dp.endswith("/") and dp != "/" else dp, dn, dialog))
        self.page.open(dialog.alert)

    def _delete_dir(self, dir_path, dir_name, dialog):
        self.page.close(dialog.alert)
        logging.debug(f"Deleting directory: [{dir_path}, {dir_name}]")
        status, response = self.comms_manager.send_message(verb=Verbs.DELETE_DIR, data=[dir_path, dir_name])
        if status == "SUCCESS":
            logging.debug(f"Directory [{dir_path}, {dir_name}] deleted successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"Directory {dir_path if dir_path != "/" else ""}/{dir_name} deleted successfully"))
        else:
            logging.debug("Directory deletion failed")
            self.page.open(error_alert(f"Directory {dir_path if dir_path != "/" else ""}/{dir_name} Deletion Failed. Please Try Again"))

    def _download_file_on_click(self, file_name):
        data = [self.current_dir, file_name]
        status, encrypted_file_bytes_nonce_tuple = self.comms_manager.send_message(verb=Verbs.DOWNLOAD_FILE, data=data)
        encrypted_file_bytes, nonce = encrypted_file_bytes_nonce_tuple
        if status == "SUCCESS":
            logging.debug("Download successful \n Decrypting file bytes...")
            file_bytes = self.file_encryption_service.decrypt_file(encrypted_file_bytes, b64decode(nonce))

            self.page.window.to_front()
            path_to_save_to = self.client_file_service.save_file_dialog(file_name)
            logging.debug(f"Path to save to: {path_to_save_to if path_to_save_to is not None or "" else 'Empty'}")
            if path_to_save_to is None or "":
                return

            self.client_file_service.save_file_to_disk(os.path.dirname(path_to_save_to), os.path.basename(path_to_save_to), file_bytes)
            logging.debug("File saved successfully")
        else:
            logging.debug("Download failed")
            self.page.open(error_alert("Download Failed. Please Try Again"))

    def _move_file_on_click(self, file_name, current_dialog_path_method=None, previous_dialog: FolderPickerAlertDialog=None):
        if current_dialog_path_method is not None:
            logging.debug("Calling current_dialog_path_method...")
            current_dialog_path = current_dialog_path_method()
        else:
            current_dialog_path = self.current_dir
        logging.debug(f"Current dialog path: {current_dialog_path}")

        dirs, files = self._get_file_list(current_dialog_path)
        subdirs = [directory["path"] for directory in dirs]
        logging.debug(f"Subdirs: {subdirs}")

        dialog = FolderPickerAlertDialog(
            page = self.page,
            title=f"Moving File: `{file_name}`",
            subdirectories=subdirs,
            current_dialog_dir=current_dialog_path,
            selected_dir_on_click_method=lambda e: self._move_file_on_click(file_name, current_dialog_path_method=(lambda: dialog.get_selected_directory_path_for_dialogs()), previous_dialog=dialog),
            on_confirm_method=lambda e: self._move_file(file_name, lambda: dialog.get_selected_directory_path_for_comms(), dialog=dialog),
        )

        self.page.open(dialog.alert)

        if previous_dialog is not None:
            self.page.close(previous_dialog.alert)

    def _move_file(self, file_name, new_file_path_method, dialog: FolderPickerAlertDialog):
        new_file_path = new_file_path_method()
        self.page.close(dialog.alert)
        data = [self.current_dir, new_file_path, file_name]
        status, response = self.comms_manager.send_message(verb=Verbs.MOVE_FILE, data=data)
        if status == "SUCCESS":
            logging.debug(f"File [{self.current_dir}, {file_name}] moved successfully to [{new_file_path}]")
            self._mini_navigator()
            self.page.open(success_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} moved successfully to {new_file_path}"))
            self._change_dir(new_file_path)
        else:
            logging.debug("File move failed")
            self.page.open(error_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} move failed. Please Try Again. (Error Code: {response})"))

    def _move_dir_on_click(self, dir_name, current_dialog_path_method=None, previous_dialog: FolderPickerAlertDialog=None):
        if current_dialog_path_method is not None:
            logging.debug("Calling current_dialog_path_method...")
            current_dialog_path = current_dialog_path_method()
        else:
            current_dialog_path = self.current_dir
        logging.debug(f"Current dialog path: {current_dialog_path}")

        dirs, files = self._get_file_list(current_dialog_path)
        subdirs = []
        for directory in dirs:
            sub_dir_path = directory["path"]
            if sub_dir_path != f"{self.current_dir if self.current_dir != "/" else ""}/{dir_name}":
                subdirs.append(sub_dir_path)

        logging.debug(f"Subdirs: {subdirs}")

        dialog = FolderPickerAlertDialog(
            page = self.page,
            title=f"Moving Folder: `{dir_name}`",
            subdirectories=subdirs,
            current_dialog_dir=current_dialog_path,
            selected_dir_on_click_method=lambda e: self._move_dir_on_click(dir_name, current_dialog_path_method=(lambda: dialog.get_selected_directory_path_for_dialogs()), previous_dialog=dialog),
            on_confirm_method=lambda e: self._move_dir(dir_name, new_dir_path_method=lambda: dialog.get_selected_directory_path_for_comms(), dialog=dialog),
        )
        self.page.open(dialog.alert)

        if previous_dialog is not None:
            self.page.close(previous_dialog.alert)

    def _move_dir(self, dir_name, new_dir_path_method, dialog: FolderPickerAlertDialog):
        new_dir_path = new_dir_path_method()
        self.page.close(dialog.alert)
        data = [self.current_dir, new_dir_path, dir_name]
        status, response = self.comms_manager.send_message(verb=Verbs.MOVE_DIR, data=data)
        if status == "SUCCESS":
            logging.debug(f"File [{self.current_dir}, {dir_name}] moved successfully to [{new_dir_path}]")
            self._mini_navigator()
            self.page.open(success_alert(f"Folder {self.current_dir if self.current_dir != "/" else ""}/{dir_name} and it's contents moved successfully to {new_dir_path}"))
            self._change_dir(new_dir_path)
        else:
            logging.debug("Folder move failed")
            self.page.open(error_alert(f"Folder {self.current_dir if self.current_dir != "/" else ""}/{dir_name} move failed. Please Try Again. (Error Code: {response})"))

    def _get_file_list(self, path):
        logging.debug("Getting file list")
        status, dirs_and_files = self.comms_manager.send_message(verb=Verbs.GET_ITEMS_LIST, data=[path])

        logging.debug(f"status: {status}")
        logging.debug(f"dirs_and_files: <{dirs_and_files}>, type: {type(dirs_and_files)}")

        dirs, files = json.loads(json.loads(dirs_and_files)["dirs_dumps"]), json.loads(json.loads(dirs_and_files)["files_dumps"])
        logging.debug(f"dirs: {dirs} \n files: {files}")
        return dirs, files

    def _change_username_on_click(self):
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Change Username:",
            subtitle="Enter your new username:",
            title_icon=ft.Icons.PERSON_ROUNDED,
            text_fields=["New Username:"],
            modal=False,
        )
        dialog.set_on_confirm_method(lambda e, d=dialog: self._change_username(get_username_method=lambda: d.get_text_field_values()[0], dialog=d))
        self.page.open(dialog.alert)

    def _change_username(self, get_username_method, dialog):
        username = get_username_method()
        self.page.close(dialog.alert)
        status, response_code = self.comms_manager.send_message(verb=Verbs.CHANGE_USERNAME, data=[username])
        if status == "SUCCESS":
            self.username = username
            self.account_container = AccountContainer(username=self.username)
            self._mini_navigator(force_animation=True)
            self.page.open(success_alert("Username updated successfully."))
        else:
            self.page.open(error_alert("Username is already taken. Please try again with another username."))

    def _change_password_on_click(self):
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Change Password:",
            subtitle="Enter your new password:",
            title_icon=ft.Icons.KEY_ROUNDED,
            text_fields=["Current Password:", "New Password:", "Confirm New Password:"],
            modal=False,
            password_fields=True
        )
        dialog.set_on_confirm_method(
            lambda e, d=dialog:
             self._change_password(
                get_current_password_method=lambda: d.get_text_field_values()[0],
                get_new_password_method=lambda: d.get_text_field_values()[1],
                get_confirm_new_password_method=lambda: d.get_text_field_values()[2],
                dialog=d
            )
        )
        self.page.open(dialog.alert)

    def _change_password(self, get_current_password_method, get_new_password_method, get_confirm_new_password_method, dialog):
        self.page.close(dialog.alert)
        current_password, new_password, confirm_new_password = get_current_password_method(), get_new_password_method(), get_confirm_new_password_method()
        if not self.passwords_service.verify_password(current_password):
            self.page.open("Current Password entered was incorrect. Please try again.")
        elif new_password != confirm_new_password:
            self.page.open(error_alert("New Password did not match Password Confirmation. Please try again."))
        elif len(new_password) < 8 or len(new_password) > 64:
            self.page.open(error_alert("Password must be between 8 and 64 characters long."))
        else:
            salt, encrypted_file_master_key, nonce = self.file_encryption_service.create_new_encryption_credentials_from_password(new_password)
            status, response_code = self.comms_manager.send_message(Verbs.CHANGE_PASSWORD, data=[self.passwords_service.hash_password(new_password), salt, encrypted_file_master_key, nonce])
            if status == "SUCCESS":
                self.page.open(success_alert("Password updated successfully."))
            else:
                self.page.open(error_alert(f"An error occured: {response_code}."))

    def _log_out(self):
        self.comms_manager.login_token = 'no_token'
        self.navigator(ViewsAndRoutesList.LOG_IN)
