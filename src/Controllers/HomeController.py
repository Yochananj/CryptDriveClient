"""
Handles events for navigating between different containers in the application,
such as Files, Account, and About. Updates the user interface and animates
transitions based on the selected container and any control events.
Incorporates animation effects for a smooth user experience during transitions.
"""


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
    """
    Encapsulates logic to manage and coordinate interactions within the home view of the application.
    This controller connects the user interface elements with backend services, facilitating navigation,
    file management, and user account interactions.

    The `HomeController` class serves as the primary handler for the application’s main interface,
    binding together its visual components and application logic. It manages navigation between
    different sections such as file management, account settings, and about information, while
    interacting with services responsible for file encryption, client communications, and
    user authentication.

    :ivar view: The view component of the home screen, responsible for rendering the UI elements.
    :type view: HomeView
    :ivar navigator: Handles navigation logic across the application screens.
    :type navigator: Any
    :ivar comms_manager: Manages communication between the client and server.
    :type comms_manager: ClientCommsManager
    :ivar file_encryption_service: Service responsible for encrypting and decrypting files.
    :type file_encryption_service: FileEncryptionService
    :ivar passwords_service: Provides functions for password-related operations.
    :type passwords_service: PasswordsService
    :ivar username: The username of the currently logged-in user.
    :type username: str
    :ivar page: Represents the current page being displayed, with UI-related properties and configurations.
    :type page: ft.Page
    :ivar container: The current active container, dynamically updated based on navigation.
    :type container: Any
    :ivar current_dir: Tracks the currently active directory path in the file container.
    :type current_dir: str
    :ivar client_file_service: Client-side service for handling file operations such as uploads and downloads.
    :type client_file_service: ClientFileService
    :ivar selected_container: The index of the currently selected container in the navigation rail.
    :type selected_container: int
    :ivar file_container: Container responsible for managing and displaying files.
    :type file_container: FileContainer
    :ivar account_container: Container managing user account information and interactions.
    :type account_container: AccountContainer
    :ivar about_container: Container showing information about the application.
    :type about_container: AboutContainer
    """
    def __init__(self,
                 page: ft.Page,
                 view: HomeView,
                 navigator,
                 comms_manager: ClientCommsManager,
                 client_file_service: ClientFileService,
                 file_encryption_service: FileEncryptionService,
                 passwords_service: PasswordsService,
                 username):
        """
        Initializes an instance of the HomeController class to manage the page, navigation,
        file system interactions, and related components in a user interface.

        :param page: The application page that the UI components are rendered on.
        :param view: The main view associated with the home screen of the application.
        :param navigator: An object responsible for handling navigation between views.
        :param comms_manager: Handles communication between the client and the server.
        :param client_file_service: Manages client-side file operations.
        :param file_encryption_service: Provides functionalities for file encryption and decryption.
        :param passwords_service: Supplies password management functionality.
        :param username: The username of the currently authenticated user.
        """
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
        """
        Sets up event handlers for various components in the user interface, linking
        navigation actions and page resizing events to respective handler methods.

        Handlers attached include:
        - Navigation rail change events to the mini navigator method.
        - Click events for the root directory navigation.
        - Page resize events to the resize handler.

        :return: None
        """
        self.view.nav_rail.on_change = self._mini_navigator
        self._attach_handlers_per_destination()
        self.page.on_resized = lambda e: self._on_resize()
        self.view.nav_rail.destinations[0].on_click = lambda e: self._change_dir("/")

    def _on_resize(self):
        """
        Handles the resize event to adjust application view dimensions and layout.

        This method dynamically adjusts the dimensions of the application components
        based on the current window size to ensure proper display and functionality.
        It also handles specific adjustments depending on the selected index of the
        navigation rail.

        :return: None
        """
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
        """
        Handles events for navigating between different containers in the application,
        such as Files, Account, and About. Updates the user interface and animates
        transitions based on the selected container and any control events.
        Incorporates animation effects for a smooth user experience during transitions.

        :param control_event: An optional argument representing a triggering event that
                              can alter the navigation behavior (default: None).
        :param force_animation: Boolean indicating whether to force animation during
                                navigation, regardless of whether the selected container
                                has changed (default: False).
        :return: None
        """
        logging.info(f"Switched to destination: {self.view.nav_rail.selected_index}")
        logging.info(f"Control event: {control_event.__dict__ if control_event else 'None'}")
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

            case 2:  # About container

                self.page.title = "CryptDrive: About"
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
        """
        Assigns specific event handlers to user interface components based on the selected
        navigation destination. This method dynamically binds actions such as file and directory
        management in the "Files" container and account-related functionalities in the "Account"
        container.

        :return: None
        """
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
        """
        Changes the current directory to the specified path and calls the mini
        navigator functionality.

        :param path: The new directory path to change to.
        :type path: str
        :return: None
        """
        self.current_dir = path
        self._mini_navigator()

    def _upload_file_button_on_click(self):
        """
        Handles the click event of the upload file button. This method interacts
        with file services to allow a user to pick a file, encrypt its contents,
        and upload it to a specified directory on the server. It also handles UI
        updates and logs the upload process.

        :return: None
        """
        self.page.window.to_front()
        file = self.client_file_service.file_picker_dialog()
        if file is None or file == "": return
        else: file = str(file)

        logging.info(f"Uploading file: {file}")
        file_name = os.path.basename(file)
        file_contents = self.client_file_service.read_file_from_disk(file)

        encrypted_file_contents, file_nonce = self.file_encryption_service.encrypt_file(file_contents)

        status, response = self.comms_manager.send_message(Verbs.CREATE_FILE, [self.current_dir, file_name, file_nonce, encrypted_file_contents])
        if status == "SUCCESS":
            logging.info("File uploaded successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} uploaded successfully"))
        else:
            logging.info("File upload failed")
            self.page.open(error_alert(f"File Upload Failed. Please Try Again. (Error Code: {response})"))

    def _rename_file_on_click(self, old_file_name):
        """
        This method creates a dialog box prompting the user to input a new name
        for the specified file. The dialog includes a confirmation method that
        triggers the internal file rename operation.

        :param old_file_name: The name of the file to be renamed.
        :type old_file_name: str
        """
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Rename File:",
            title_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED,
            subtitle=f"Enter the new file name for the file '{old_file_name}':",
            text_fields=["New File Name:"]
        )
        dialog.set_on_confirm_method(lambda e: self._rename_file(old_file_name, dialog=dialog))
        self.page.open(dialog.alert)

    def _rename_file(self, old_file_name, dialog, file_extension_change_dialog=None, override_file_extension: bool = False):
        """
        Renames a file by interacting with a dialog interface and handling validations for the new file name.

        This function performs several checks on the new file name such as ensuring it is non-empty, does not contain invalid
        characters (slashes, pipes), and handles cases where the file extension needs to be modified. It also provides a
        confirmation dialog if the new file name has a different extension from the old one, ensuring user confirmation for
        this action. The renaming operation communicates with a backend system to complete the action.

        :param old_file_name: The current name of the file to be renamed.
        :type old_file_name: str
        :param dialog: A dialog interface object containing the user input for the new file name.
        :type dialog: Any
        :param file_extension_change_dialog: A dialog interface for confirming a change in file extension. Optional.
        :type file_extension_change_dialog: Any, optional
        :param override_file_extension: A flag indicating whether to override warnings related to file extension changes.
            Defaults to False.
        :type override_file_extension: bool
        :return: None
        """
        new_file_name = dialog.get_text_field_values()[0]
        logging.info(f"Current dir: {self.current_dir}")
        logging.info(f"Old file name: {old_file_name}")
        logging.info(f"New file name: {new_file_name}")
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
                logging.info("File renamed successfully")
                self._mini_navigator()
                self.page.open(success_alert(f"File {old_file_name} renamed successfully to {new_file_name}"))
            else:
                logging.info("File renaming failed")
                self.page.open(error_alert(f"File renaming failed. Please Try Again. (Error Code: {response})"))

    def _rename_dir_on_click(self, old_dir_name):
        """
        Triggers the renaming process for a directory when the associated action
        is performed, such as a button click. It initiates a dialog that allows
        the user to input a new directory name, validates the input, and confirms
        the renaming operation.

        :param old_dir_name: The current name of the directory that is to be
                             renamed.
        :type old_dir_name: str
        :return: None
        """
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Rename Dir:",
            title_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED,
            subtitle=f"Enter the new file name for the file '{old_dir_name}':",
            text_fields=["New File Name:"]
        )
        dialog.set_on_confirm_method(lambda e: self._rename_dir(old_dir_name, dialog=dialog))
        self.page.open(dialog.alert)

    def _rename_dir(self, old_dir_name, dialog: TextFieldAlertDialog):
        """
        Renames a directory from `old_dir_name` to a new name inputted via the provided
        dialog. Ensures the new name adheres to specific formatting rules (non-empty,
        alphanumeric, and no special characters) before proceeding with the renaming
        process. Displays appropriate alerts for validation errors or operation status.

        :param old_dir_name: The current name of the directory to be renamed.
        :type old_dir_name: str
        :param dialog: A dialog object used to capture the new directory name input
            and display alerts for user feedback.
        :type dialog: object

        :return: None
        """
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
            logging.info("Directory renamed successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"Directory {self.current_dir if self.current_dir != "/" else ""}/{old_dir_name} renamed successfully to {self.current_dir if self.current_dir != "/" else ""}/{new_dir_name}"))
        else:
            logging.info("Directory renaming failed")
            self.page.open(error_alert(f"Directory renaming failed. Please Try Again. (Error Code: {response}"))

    def _create_dir_button_on_click(self):
        """
        Handles the 'create directory' button click event by displaying a dialog
        to prompt the user for a new directory name. Upon confirmation, it triggers
        the directory creation process.

        :raise RuntimeError: If the dialog fails to open or set a confirmation method.
        """
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Create New Directory:",
            title_icon=ft.Icons.CREATE_NEW_FOLDER_ROUNDED,
            subtitle="Enter the name of the new directory:",
            text_fields=["Directory Name:"]
        )
        dialog.set_on_confirm_method(lambda e: self._create_dir_confirm_on_click(dialog))
        self.page.open(dialog.alert)

    def _create_dir_confirm_on_click(self, dialog):
        """
        Handles the confirmation logic for creating a directory. Validates the directory name for
        emptiness and invalid characters, communicates with the server to create the directory, and
        displays appropriate success or error messages based on the operation outcome.

        :param dialog: The dialog object containing the user input for the directory name.
        :type dialog: Dialog
        :return: None
        """
        dir_name = dialog.get_text_field_values()[0]
        self.page.close(dialog.alert)

        logging.info(f"Current dir: {self.current_dir}")
        logging.info(f"Dir name: {dir_name}")

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
            logging.info("Directory created successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"Directory {self.current_dir if self.current_dir != "/" else ""}/{dir_name} created successfully"))
        else:
            logging.info("Directory creation failed")
            self._mini_navigator()
            self.page.open(error_alert(f"Directory name already taken. Please try again with a different name. (Error Code: {response})"))

    def _delete_file_on_click(self, file_name):
        """
        This method displays a confirmation dialog to the user before proceeding with the
        deletion of the file on which the delete button was clicked. If the user confirms,
        it invokes the file deletion process internally.

        :param file_name: Name of the file to be deleted.
        :type file_name: str
        :return: None
        """
        dialog = CancelConfirmAlertDialog(
            page=self.page,
            title="Confirm File Deletion",
            title_icon=ft.Icons.DELETE_ROUNDED,
            subtitle=f"Are you sure you want to delete the file `{file_name}`?"
        )
        dialog.set_on_confirm_method(lambda e, fn=file_name, d=dialog: self._delete_file(fn, d))
        self.page.open(dialog.alert)

    def _delete_file(self, file_name: str, dialog: CancelConfirmAlertDialog):
        """
        Deletes a specified file from the current directory and provides user feedback based
        on the success or failure of the operation. It also updates the UI and logs the
        operation details.

        :param file_name: Name of the file to be deleted.
        :type file_name: str
        :param dialog: An instance of CancelConfirmAlertDialog used to confirm file deletion.
        :type dialog: CancelConfirmAlertDialog
        :return: None
        """
        self.page.close(dialog.alert)
        logging.info(f"Deleting file: {self.current_dir if self.current_dir != "/" else ""}/{file_name}")
        status, response = self.comms_manager.send_message(verb=Verbs.DELETE_FILE, data=[self.current_dir, file_name])
        if status == "SUCCESS":
            logging.info(f"File [{self.current_dir}, {file_name}] deleted successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} deleted successfully"))
        else:
            logging.info("File deletion failed")
            self.page.open(error_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} Deletion Failed. Please Try Again"))

    def _delete_dir_on_click(self, directory: FolderTile):
        """
        Handles the displaying of a dialog to confirm deletion of a specified directory.

        A confirmation dialog is displayed to the user, asking for confirmation to
        delete the specified directory. If the user confirms, the method triggers
        the deletion process for the given directory.

        :param directory: The folder tile representing the directory to be deleted.
        :type directory: FolderTile
        """
        dialog = CancelConfirmAlertDialog(
            page=self.page,
            title="Confirm Directory Deletion",
            title_icon=ft.Icons.DELETE_ROUNDED,
            subtitle=f"Are you sure you want to delete the directory `{directory.name}`?"
        )
        dialog.set_on_confirm_method(lambda e, dp = directory.path, dn = directory.name: self._delete_dir(dp[:-1] if dp.endswith("/") and dp != "/" else dp, dn, dialog))
        self.page.open(dialog.alert)

    def _delete_dir(self, dir_path, dir_name, dialog: CancelConfirmAlertDialog):
        """
        Deletes a directory by sending a delete request and handles the response appropriately.

        This function is responsible for interacting with the communication manager to
        delete a specified directory. It also manages related user interface updates
        based on the success or failure of the operation.

        :param dir_path: The absolute path of the directory to delete.
        :type dir_path: str
        :param dir_name: The name of the directory to delete.
        :type dir_name: str
        :param dialog: The dialog object that triggered the operation. Used to handle
            user notifications or alerts.
        :type dialog: object
        :return: None
        """
        self.page.close(dialog.alert)
        logging.info(f"Deleting directory: [{dir_path}, {dir_name}]")
        status, response = self.comms_manager.send_message(verb=Verbs.DELETE_DIR, data=[dir_path, dir_name])
        if status == "SUCCESS":
            logging.info(f"Directory [{dir_path}, {dir_name}] deleted successfully")
            self._mini_navigator()
            self.page.open(success_alert(f"Directory {dir_path if dir_path != "/" else ""}/{dir_name} deleted successfully"))
        else:
            logging.info("Directory deletion failed")
            self.page.open(error_alert(f"Directory {dir_path if dir_path != "/" else ""}/{dir_name} Deletion Failed. Please Try Again"))

    def _download_file_on_click(self, file_name):
        """
        Downloads a file from the server when triggered by a click event. This method
        handles the communication with the server to request the file, decryption of the
        received file bytes, and saving the file to a specified location on the client's
        system.

        :param file_name: The name of the file to be downloaded.
        :type file_name: str
        :return: None
        """
        data = [self.current_dir, file_name]
        status, encrypted_file_bytes_nonce_tuple = self.comms_manager.send_message(verb=Verbs.DOWNLOAD_FILE, data=data)
        encrypted_file_bytes, nonce = encrypted_file_bytes_nonce_tuple
        if status == "SUCCESS":
            logging.info("Download successful \n Decrypting file bytes...")
            file_bytes = self.file_encryption_service.decrypt_file(encrypted_file_bytes, b64decode(nonce))

            self.page.window.to_front()
            path_to_save_to = self.client_file_service.save_file_dialog(file_name)
            logging.info(f"Path to save to: {path_to_save_to if path_to_save_to is not None or "" else 'Empty'}")
            if (path_to_save_to is None) or path_to_save_to == "":
                return

            self.client_file_service.save_file_to_disk(os.path.dirname(path_to_save_to), os.path.basename(path_to_save_to), file_bytes)
            logging.info("File saved successfully")
        else:
            logging.info("Download failed")
            self.page.open(error_alert("Download Failed. Please Try Again"))

    def _move_file_on_click(self, file_name, current_dialog_path_method=None, previous_dialog: FolderPickerAlertDialog=None):
        """
        Handles the operation of displaying a dialog for the user to choose a new location
        for a file when a click action is triggered.

        This method facilitates selecting a new location for a file through an interactive
        folder picker dialog. It updates the current directory path based on the provided
        method or the internal state and ensures that the corresponding file is moved to the
        selected directory upon confirmation.

        :param file_name: The name of the file to move.
        :type file_name: str
        :param current_dialog_path_method: Optional. A callable that returns the current dialog path.
        :type current_dialog_path_method: Callable or None
        :param previous_dialog: Optional. The previous `FolderPickerAlertDialog` instance to be closed
                                upon opening the new dialog.
        :type previous_dialog: FolderPickerAlertDialog or None
        :return: None
        """
        if current_dialog_path_method is not None:
            logging.info("Calling current_dialog_path_method...")
            current_dialog_path = current_dialog_path_method()
        else:
            current_dialog_path = self.current_dir
        logging.info(f"Current dialog path: {current_dialog_path}")

        dirs, files = self._get_file_list(current_dialog_path)
        subdirs = [directory["path"] for directory in dirs]
        logging.info(f"Subdirs: {subdirs}")

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
        """
        Handles the process of moving a file from its current location to a specified new
        location on the server. The operation interacts with a remote communications
        manager, displays success or failure alerts to the user, and updates the
        current directory context as required.

        :param file_name: The name of the file to be moved.
        :type file_name: str
        :param new_file_path_method: A callable that determines the new file path.
        :type new_file_path_method: Callable[[], str]
        :param dialog: An instance of `FolderPickerAlertDialog` used in the file
                       picking operations.
        :type dialog: FolderPickerAlertDialog
        :return: None
        """
        new_file_path = new_file_path_method()
        self.page.close(dialog.alert)
        data = [self.current_dir, new_file_path, file_name]
        status, response = self.comms_manager.send_message(verb=Verbs.MOVE_FILE, data=data)
        if status == "SUCCESS":
            logging.info(f"File [{self.current_dir}, {file_name}] moved successfully to [{new_file_path}]")
            self._mini_navigator()
            self.page.open(success_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} moved successfully to {new_file_path}"))
            self._change_dir(new_file_path)
        else:
            logging.info("File move failed")
            self.page.open(error_alert(f"File {self.current_dir if self.current_dir != "/" else ""}/{file_name} move failed. Please Try Again. (Error Code: {response})"))

    def _move_dir_on_click(self, dir_name, current_dialog_path_method=None, previous_dialog: FolderPickerAlertDialog=None):
        """
        Handles displaying a dialog to allow the user to select a new location for a folder
        through a user interface for selecting directories.

        This method handles the logic for building a dialog-based UI that allows the user
        to select a new location for a specified directory. It maintains references to
        current and previous dialogs to ensure seamless navigation during the folder move
        operation.

        :param dir_name: Name of the directory to be moved.
        :type dir_name: str
        :param current_dialog_path_method: Method reference to retrieve the current dialog's
            directory path. If None, the method will use the object's current_dir attribute.
        :type current_dialog_path_method: Callable[[], str] or None
        :param previous_dialog: Reference to the previous dialog, which is closed if a new
            dialog is opened. If None, no previous dialog is processed.
        :type previous_dialog: FolderPickerAlertDialog or None
        :return: None
        """
        if current_dialog_path_method is not None:
            logging.info("Calling current_dialog_path_method...")
            current_dialog_path = current_dialog_path_method()
        else:
            current_dialog_path = self.current_dir
        logging.info(f"Current dialog path: {current_dialog_path}")

        dirs, files = self._get_file_list(current_dialog_path)
        subdirs = []
        for directory in dirs:
            sub_dir_path = directory["path"]
            if sub_dir_path != f"{self.current_dir if self.current_dir != "/" else ""}/{dir_name}":
                subdirs.append(sub_dir_path)

        logging.info(f"Subdirs: {subdirs}")

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
        """
        Moves a directory from the current location to a new location on the server. The target
        directory is specified by its name, and the new location is determined via a provided method.
        It communicates with a backend service to perform the operation and handles the
        response to display appropriate alerts.

        :param dir_name: Name of the directory to be moved.
        :type dir_name: str
        :param new_dir_path_method: A callable that determines the new directory path.
        :type new_dir_path_method: Callable[[], str]
        :param dialog: The dialog instance used for displaying the folder picker alert.
        :type dialog: FolderPickerAlertDialog
        :return: None
        """
        new_dir_path = new_dir_path_method()
        self.page.close(dialog.alert)
        data = [self.current_dir, new_dir_path, dir_name]
        status, response = self.comms_manager.send_message(verb=Verbs.MOVE_DIR, data=data)
        if status == "SUCCESS":
            logging.info(f"File [{self.current_dir}, {dir_name}] moved successfully to [{new_dir_path}]")
            self._mini_navigator()
            self.page.open(success_alert(f"Folder {self.current_dir if self.current_dir != "/" else ""}/{dir_name} and it's contents moved successfully to {new_dir_path}"))
            self._change_dir(new_dir_path)
        else:
            logging.info("Folder move failed")
            self.page.open(error_alert(f"Folder {self.current_dir if self.current_dir != "/" else ""}/{dir_name} move failed. Please Try Again. (Error Code: {response})"))

    def _get_file_list(self, path):
        """
        Retrieves the list of directories and files for the given path by communicating with the comms manager.
        Processes and parses the response to extract and return directories and files information.

        :param path: Path for which the directories and files need to be listed.
        :type path: str
        :return: A tuple containing two lists - the first list contains directories and the second list contains files.
        :rtype: tuple[list[str], list[str]]
        """
        logging.info("Getting file list")
        status, dirs_and_files = self.comms_manager.send_message(verb=Verbs.GET_ITEMS_LIST, data=[path])

        logging.info(f"status: {status}")
        logging.info(f"dirs_and_files: <{dirs_and_files}>, type: {type(dirs_and_files)}")

        dirs, files = json.loads(json.loads(dirs_and_files)["dirs_dumps"]), json.loads(json.loads(dirs_and_files)["files_dumps"])
        logging.info(f"dirs: {dirs} \n files: {files}")
        return dirs, files

    def _change_username_on_click(self):
        """
        Handles the process of initiating a username change dialog when triggered by a user action.

        This method creates an instance of a `TextFieldAlertDialog`, which prompts the user to input a
        new username. Upon confirming, it invokes a defined method to process the username change.

        :return: None
        """
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Change Username:",
            subtitle="Enter your new username:",
            title_icon=ft.Icons.PERSON_ROUNDED,
            text_fields=["New Username:"]
        )
        dialog.set_on_confirm_method(lambda e, d=dialog: self._change_username(get_username_method=lambda: d.get_text_field_values()[0], dialog=d))
        self.page.open(dialog.alert)

    def _change_username(self, get_username_method, dialog):
        """
        Changes the username of the user by interacting with the specified dialog and executing the provided
        method to get the new username. Sends an update request and updates the UI accordingly based
        on the success or failure of the operation.

        :param get_username_method: A callable that retrieves the new username the user wants to set.
        :type get_username_method: Callable[[], str]
        :param dialog: The dialog object that facilitates the user interaction during the operation.
        :type dialog: Any
        :return: None
        """
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
        """
        Handles the logic for opening a dialog to change the user's password. Presents a UI for the user to
        input their current password, new password, and confirmation of the new password. Configures the
        dialog to execute the password change logic upon confirmation.

        :param self: Represents the instance of the class holding this method.

        :return: None
        """
        dialog = TextFieldAlertDialog(
            page=self.page,
            title="Change Password:",
            subtitle="Enter your new password:",
            title_icon=ft.Icons.KEY_ROUNDED,
            text_fields=["Current Password:", "New Password:", "Confirm New Password:"],
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
        """
        Handles the process of changing the user's password, including validation of the current
        password, confirmation of the new password, ensuring the password meets length
        requirements, and updating the backend system with the new password.

        :param get_current_password_method: A callable that returns the current password entered
                                             by the user.
        :type get_current_password_method: Callable[[], str]
        :param get_new_password_method: A callable that returns the new password entered by
                                         the user.
        :type get_new_password_method: Callable[[], str]
        :param get_confirm_new_password_method: A callable that returns the password confirmation
                                                 entered by the user.
        :type get_confirm_new_password_method: Callable[[], str]
        :param dialog: The dialog instance that contains the alert to close.
        :type dialog: Dialog
        :return: None
        """
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
            data = [self.passwords_service.hash_password(current_password), self.passwords_service.hash_password(new_password), salt, encrypted_file_master_key, nonce]
            status, response_code = self.comms_manager.send_message(Verbs.CHANGE_PASSWORD, data=data)
            if status == "SUCCESS":
                self.page.open(success_alert("Password updated successfully."))
            else:
                self.page.open(error_alert(f"An error occured: {response_code}."))

    def _log_out(self):
        """
        Logs the user out by invalidating the login token and navigating back to
        the login screen.

        :return: None
        """
        self.comms_manager.login_token = 'no_token'
        self.navigator(ViewsAndRoutesList.LOG_IN)
