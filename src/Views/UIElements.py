import logging

import flet as ft

from Dependencies.Constants import crypt_drive_blue_semilight, crypt_drive_purple, crypt_drive_blue_medium_light


class FileTile:
    """
    Represents a visual tile component for managing a file in the application.

    The FileTile class encapsulates the representation and functionality of a file
    tile in the user interface. It provides controls for various file operations
    such as downloading, renaming, moving, and deleting. Each file tile visually
    displays file details like its name and size, and includes interactive buttons
    for user actions.

    :ivar name: The name of the file represented by this tile.
    :type name: str
    :ivar size: The size of the file in bytes.
    :type size: int
    :ivar tile: A container object holding the visual representation of the file
        tile, consisting of file details and operation buttons.
    :type tile: ft.Container
    """
    def __init__(self, file_name, file_size):
        """
        Represents a file with its metadata and associated user-interaction controls such as
        download, rename, move, and delete. This class creates a visual tile representation of
        the file, including an icon, file name, file size, and interactive buttons for file
        operations.

        :param file_name: The name of the file.
        :type file_name: str
        :param file_size: The size of the file (in bytes).
        :type file_size: int
        """
        self.name = file_name
        self.size = file_size
        self.download = ft.IconButton(
            ft.Icons.FILE_DOWNLOAD_OUTLINED,
            tooltip="Download File"
        )
        self.rename = ft.IconButton(
            ft.Icons.EDIT,
            tooltip="Rename File"
        )
        self.move = ft.IconButton(
            ft.Icons.DRIVE_FILE_MOVE_ROUNDED,
            tooltip="Move File"
        )
        self.delete = ft.IconButton(
            ft.Icons.DELETE,
            tooltip="Delete File"
        )
        self.tile = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INSERT_DRIVE_FILE),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls = [
                                    ft.Text(self.name, font_family="Aeonik Bold", size=20),
                                    ft.Text(f"Size: {self.size} bytes", font_family="Aeonik", size=16)
                                ],
                                height=40,
                                expand = False
                            )
                        ], expand = True
                    ),
                    self.download,
                    self.move,
                    self.rename,
                    self.delete,
                ],
                expand=False
            ),
            border_radius=10,
            bgcolor=crypt_drive_blue_semilight,
            padding=ft.padding.only(left=10, right=10, top=10, bottom=10),
            expand=False
        )


class FolderTile:
    """
    Represents a folder tile with functionality and display customizations.

    This class is used for creating a visual representation of folders with customization
    options for compact view, regular folder icon, and hiding the folder path. It offers
    controls for managing folders, such as moving, renaming, and deleting. It determines
    the appropriate visual elements and interactions based on the provided configuration.

    :ivar name: The name of the folder extracted from the given path.
    :type name: str
    :ivar path: The path of the folder (excluding the folder name itself).
    :type path: str
    :ivar items: The count of items contained within the folder.
    :type items: int
    :ivar parent_icon: Icon representing the parent folder or root indicator.
    :type parent_icon: Icon
    :ivar tooltip: Tooltip text providing the context of the tile (e.g., root folder message).
    :type tooltip: str
    :ivar is_root: Indicates whether the folder is the root directory.
    :type is_root: bool
    :ivar move: Button to move the folder.
    :type move: IconButton
    :ivar rename: Button to rename the folder.
    :type rename: IconButton
    :ivar delete: Button to delete the folder.
    :type delete: IconButton
    :ivar tile: The visual container displaying folder details, icons, and controls.
    :type tile: FloatingActionButton or Container
    """
    def __init__(self, path, item_count, compact_tile=False, regular_folder_icon=False, hide_path=False):
        """
        Represents a folder tile component for a file management UI, allowing folder-related
        operations such as movement, renaming, and deletion. The component can be customized
        to have a compact or regular design and displays details such as the folder name and
        item count.

        :param path: The file system path of the folder. Must be a non-empty string.
        :type path: str
        :param item_count: The total number of items in the folder (files, subfolders).
        :type item_count: int
        :param compact_tile: Optional; if True, uses a more compact tile representation. Defaults to False.
        :type compact_tile: bool, optional
        :param regular_folder_icon: Optional; if True, displays a basic folder icon for this tile. Defaults to False.
        :type regular_folder_icon: bool, optional
        :param hide_path: Optional; if True, hides the folder path from the UI display. Defaults to False.
        :type hide_path: bool, optional
        """
        self.name = path.split("/")[-1]

        if self.name == "":
            self.path = "/"
        else:
            self.path = path[:-len(self.name)]

        self.items = item_count
        self.parent_icon = ft.Icons.DRIVE_FOLDER_UPLOAD_ROUNDED
        self.tooltip = "Click to return to Parent Folder"
        self.is_root = False

        self.move = ft.IconButton(
            ft.Icons.DRIVE_FILE_MOVE_ROUNDED,
            tooltip="Move File"
        )
        self.rename = ft.IconButton(
            icon=ft.Icons.EDIT,
            tooltip="Rename Folder"
        )
        self.delete = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Delete Folder"
        )

        if self.path == "/" and self.name == "":
            self.is_root = True
            self.parent_icon = ft.Icons.HOME_ROUNDED
            self.tooltip = "Already at root folder"

        if regular_folder_icon: self.parent_icon = ft.Icons.FOLDER_ROUNDED


        if compact_tile:
            self.tile=ft.FloatingActionButton(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(self.parent_icon, color=crypt_drive_purple),
                            ft.Text(self.path if not hide_path else "", font_family="Aeonik Bold" if not self.is_root else "Aeonik Black", size=20),
                            ft.Text(self.name, font_family="Aeonik Black", size=20)
                        ],
                    ),
                    tooltip=self.tooltip,
                    border_radius=10,
                    bgcolor=crypt_drive_blue_semilight,
                    padding=ft.padding.all(10),
                    expand=True,
                ),
                bgcolor=crypt_drive_blue_semilight,
                elevation=0,
                expand=True,
                height=50,
            )
            if self.is_root:
                self.tile.disabled = True
        else:
            self.tile = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FOLDER),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(self.name, font_family="Aeonik Bold", size=20),
                                        ft.Text(f"{self._get_items_string(self.items)}", font_family="Aeonik", size=16)
                                    ],
                                    height=40,
                                    expand=False
                                )
                            ],
                            expand=True,
                        ),
                        self.move,
                        self.rename,
                        self.delete,
                    ],
                    expand=False
                ),
                border_radius=10,
                bgcolor=crypt_drive_blue_semilight,
                padding=ft.padding.only(left=10, right=10, top=10, bottom=12),
                tooltip="Click to open folder",
            )

    def _get_items_string(self, item_count: int):
        """
        Generates a string representation of the item count. If the count is one,
        it returns "1 item". Otherwise, it returns the count followed by "items".

        :param item_count: The number of items to generate the string for.
        :type item_count: int
        :return: A string describing the quantity of items.
        :rtype: str
        """
        if item_count == 1:
            return "1 item"
        else:
            return f"{item_count} items"


def error_alert(error_message: str):
    """
    Provides a reusable utility to generate an error alert snack bar UI component. The snack bar
    utilizes the specified error message for displaying an error-related notification. It is visually
    configured to use a red color theme to signify an error and floats over the application UI with
    a custom margin and shape.

    :param error_message: The error message to be displayed in the snack bar notification.
    :type error_message: str

    :return: An instance of a snack bar UI component configured with the provided error message
             and styled to indicate an error notification.
    :rtype: ft.SnackBar
    """
    return ft.SnackBar(
        duration=5000,
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.CLOSE_ROUNDED, color=ft.Colors.RED),
                      ft.Text(error_message, color=ft.Colors.RED)],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        ),
        behavior=ft.SnackBarBehavior.FLOATING,
        bgcolor=ft.Colors.RED_100,
        shape=ft.ContinuousRectangleBorder(radius=10),
        margin=ft.margin.all(10),
    )

def success_alert(success_message: str):
    """
    Displays a success notification with a snackbar containing a message
    and decorative elements like an icon and background color. The success
    alert persists for a fixed duration and floats above other UI elements.

    :param success_message: The message to display inside the success snackbar.
    :type success_message: str
    :return: A SnackBar instance pre-configured with the success message, styles,
        and visual properties.
    :rtype: ft.SnackBar
    """
    return ft.SnackBar(
        duration=5000,
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.CHECK_ROUNDED, color=ft.Colors.GREEN),
                      ft.Text(success_message, color=ft.Colors.GREEN)],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        ),
        behavior=ft.SnackBarBehavior.FLOATING,
        bgcolor=ft.Colors.GREEN_100,
        shape=ft.ContinuousRectangleBorder(radius=10),
        margin=ft.margin.all(10),
    )


class TextFieldAlertDialog:
    """
    Represents a dialog with text fields that allows user interactions such as
    entering text inputs and confirming or canceling operations.

    This class provides an alert dialog with specified text input fields, configurable
    title, subtitle, and behavior on confirmation or cancellation. It primarily serves
    to capture user inputs through a graphical text field interface. It can be customized
    to include password fields, modal behavior, and other application-specific adjustments.

    :ivar text_fields: A container for managing the input text fields displayed in the dialog.
    :type text_fields: ft.Column
    :ivar content: The main content of the dialog, including text fields and subtitle.
    :type content: ft.Container
    :ivar alert: The alert dialog instance configured with title, subtitle,
         content, and optional modal behavior.
    :type alert: ft.AlertDialog
    :ivar cancel: The cancel button of the dialog that closes the dialog on click.
    :type cancel: ft.TextButton
    :ivar confirm: The confirm button of the dialog that triggers the confirmation
         event, enabled when all text fields are filled.
    :type confirm: ft.TextButton
    """
    def __init__(
            self,
            page: ft.Page,
            title: str,
            title_icon: ft.Icons,
            subtitle: str,
            text_fields: list[str],
            modal: bool = False,
            password_fields: list[bool] = False,
            ):
        """
        Initializes the class and creates an alert dialog for user input, with configurable
        text fields and behaviors.

        :param page: The instance of the Flet Page where the dialog will be displayed.
        :param title: The title of the alert dialog.
        :param title_icon: The icon displayed alongside the dialog title.
        :param subtitle: The subtitle displayed in the alert dialog, providing additional
           context or instructions.
        :param text_fields: A list of labels for the text fields in the dialog.
        :param modal: If set to True, the alert dialog will appear as a modal, preventing
           interaction with other parts of the UI until the dialog is dismissed.
        :param password_fields: If set to True, all text fields will mask input as
           password fields.
        """

        self.text_fields = ft.Column(
            controls=[],
        )

        for i in range(len(text_fields)):
            self.text_fields.controls.append(
                ft.TextField(
                    label=text_fields[i],
                    password=password_fields if password_fields == False else password_fields[i],
                    can_reveal_password=True
                )
            )

        self.content = ft.Container(
            content=
            ft.Column(
                controls=[
                    ft.Text(subtitle, font_family="Aeonik"),
                    self.text_fields
                ],
            ),
            alignment=ft.Alignment(0,0),
            width=400,
            height = 90 + 50 * (len(text_fields) - 1),
        )
        self.alert = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(title_icon, color=crypt_drive_purple),
                ft.Text(title, font_family="Aeonik Bold")
                ],
            ),
            modal=modal,
            content=self.content,
            bgcolor=crypt_drive_blue_semilight,

        )
        self.cancel = ft.TextButton(text="Cancel", on_click=lambda e: page.close(self.alert))
        self.confirm = ft.TextButton(text="Confirm", disabled=True)
        self.alert.actions=[self.cancel, self.confirm]

        for text_field in self.text_fields.controls:
            text_field.on_change = lambda e: self._update_confirm_button_status()

    def set_on_confirm_method(self, method):
        """
        Sets the method to execute when the confirm button is clicked.

        :param method: Callable function to be executed upon confirm button click.
        :type method: Callable
        """
        self.confirm.on_click = method

    def get_text_field_values(self) -> list[str]:
        """
        Extracts the values from text fields in the controls list.

        This method iterates through all text fields in the `controls` attribute and
        retrieves their `value` properties, returning them as a list.

        :return: A list of string values extracted from the text fields.
        :rtype: list[str]
        """
        return [text_field.value for text_field in self.text_fields.controls]

    def _update_confirm_button_status(self):
        """
        Updates the status of the confirm button.

        This method adjusts the disabled state of the confirm button based on whether
        all required text fields have a value. It ensures that the button is only
        enabled when all conditions are met. After updating the button status, it
        refreshes the alert view to reflect any changes.

        :return: None
        """
        self.confirm.disabled = not self._do_all_text_fields_have_a_value()
        self.alert.update()

    def _do_all_text_fields_have_a_value(self):
        """
        Checks whether all text fields in the `text_fields` collection have a value.

        This method iterates through the `controls` of `text_fields` and checks if any
        of the `value` attributes are empty. If all fields have non-empty `value` attributes,
        the method returns True; otherwise, it returns False.

        :return: True if all text fields have a value, otherwise False.
        :rtype: bool
        """
        for text_field in self.text_fields.controls:
            if text_field.value == "":
                return False
        else:
            return True


class CancelConfirmAlertDialog:
    """
    Represents a dialog for cancel or confirm actions.

    This class handles the creation and presentation of an alert dialog with customizable
    title, subtitle, and action buttons. The dialog can be used in conjunction with various
    application workflows to confirm or cancel actions.

    :ivar alert: The constructed alert dialog object containing the title, subtitle,
        button actions, and styling.
    :type alert: ft.AlertDialog
    :ivar cancel: The button element representing the "Cancel" action within the dialog.
    :type cancel: ft.TextButton
    :ivar confirm: The button element representing the "Confirm" action within the dialog.
    :type confirm: ft.TextButton
    """
    def __init__(
            self,
            page: ft.Page,
            title: str,
            title_icon: ft.Icons,
            subtitle: str,
            modal=False):
        """
        Initializes the class with an alert dialog containing a title, subtitle, and action
        buttons. The dialog can be modal and styled with the provided parameters.

        :param page: The page object where the alert dialog will be displayed.
        :type page: ft.Page
        :param title: The title text to be displayed in the alert dialog.
        :type title: str
        :param title_icon: The icon to be displayed alongside the title text.
        :type title_icon: ft.Icons
        :param subtitle: The subtitle text to be displayed in the alert dialog.
        :type subtitle: str
        :param modal: Specifies whether the alert dialog should be modal. Defaults to False.
        :type modal: bool
        """

        self.alert = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(title_icon, color=crypt_drive_purple),
                ft.Text(title, font_family="Aeonik Bold")
            ]),
            modal=modal,
            content=ft.Container(ft.Text(subtitle, font_family="Aeonik"), width=500, expand=False),
            bgcolor=crypt_drive_blue_semilight,

        )
        self.cancel = ft.TextButton(text="Cancel", on_click=lambda e: page.close(self.alert))
        self.confirm = ft.TextButton(text="Confirm")
        self.alert.actions = [self.cancel, self.confirm]


    def set_on_confirm_method(self, method):
        """
        Sets the method to be called when the confirm button is clicked.

        :param method: The callable to be executed when the confirm button's click
            event is triggered.
        :type method: Callable
        """
        self.confirm.on_click = method

class FolderPickerAlertDialog:
    """
    Represents a dialog for selecting a folder from a list of directories.

    The class is designed to provide a user interface for navigating and selecting a folder.
    It dynamically updates the current view based on folder selection and provides functionality
    for confirming or canceling the action. The dialog is customizable with an alert title and
    callbacks for handling folder selection or final confirmation.

    :ivar current_dir: Represents the current directory being displayed in the dialog.
    :type current_dir: FolderTile
    :ivar dir_list: A list of FolderTile objects representing the selectable subdirectories within the dialog.
    :type dir_list: list[FolderTile]
    :ivar subtitle: Displays the currently selected folder's path and name as a subtitle in the dialog.
    :type subtitle: ft.Text
    :ivar alert: The main alert dialog displaying available directories and selection options.
    :type alert: ft.AlertDialog
    :ivar cancel: A button that allows the user to cancel the folder selection process.
    :type cancel: ft.TextButton
    :ivar confirm: A button that allows the user to confirm the selected folder.
    :type confirm: ft.TextButton
    :ivar selected_dir: The FolderTile object representing the currently selected directory.
    :type selected_dir: FolderTile
    :ivar selected_dir_on_click_method: A callback method triggered when a folder tile is clicked.
    :type selected_dir_on_click_method: callable
    """
    def __init__(self, page: ft.Page, title: str, subdirectories, current_dialog_dir, selected_dir_on_click_method, on_confirm_method):
        """
        Initializes an instance of the dialog for selecting a directory.

        This constructor initializes the directory selection dialog and creates the
        visual layout comprising various components such as the current directory
        tile, subdirectory tiles, selection subtitle, alert dialog, and additional
        actions like cancel and confirm. It also sets up the behavior for selecting
        directories and handling user interactions.

        :param page: The main user interface page where the dialog will be attached.
        :param title: The title for the folder selection dialog.
        :param subdirectories: Iterable of subdirectories to be displayed in the dialog.
        :param current_dialog_dir: The current directory to be displayed at the top of
            the dialog hierarchy.
        :param selected_dir_on_click_method: The method to invoke when a directory is
            selected.
        :param on_confirm_method: The method to invoke when the "Confirm" button is
            clicked.
        """

        self.current_dir = FolderTile(current_dialog_dir, 0, True)
        self.current_dir.tile.disabled = False
        self.dir_list: list[FolderTile] = [self.current_dir]

        for directory in subdirectories:
            self.dir_list.append(FolderTile(directory, 0, True, True, hide_path=True))

        rows_list = []
        for directory in self.dir_list:
            rows_list.append(ft.Row(controls=[directory.tile]))

        self.subtitle=ft.Text(f"Selected folder: {self.current_dir.path + self.current_dir.name}", font_family="Aeonik")
        self.alert = ft.AlertDialog(
            title=ft.Column(
                [ft.Row([ft.Icon(ft.Icons.DRIVE_FILE_MOVE_ROUNDED, color=crypt_drive_purple), ft.Text(title, font_family="Aeonik Bold")]), self.subtitle]
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=rows_list,
                    scroll=True,
                ),
                width=600,
                padding=ft.padding.all(10),
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            bgcolor=crypt_drive_blue_semilight,
        )
        self.cancel = ft.TextButton(text="Cancel", on_click=lambda e: page.close(self.alert))
        self.confirm = ft.TextButton(text="Confirm", on_click=on_confirm_method)
        self.alert.actions = [self.cancel, self.confirm]

        self.selected_dir: FolderTile = self.current_dir
        self.selected_dir_on_click_method = selected_dir_on_click_method
        self._update_selected_dir(self.current_dir)

    def _update_selected_dir(self, directory: FolderTile):
        """
        Updates the selected directory and modifies the attributes of the folder tiles based
        on the selected directory. Ensures that the visual representation and event handlers
        of directory tiles are updated dynamically upon selection.

        :param directory: The `FolderTile` object representing the directory that is selected.
        :type directory: FolderTile
        :return: None
        """
        logging.info(f"Selected dir: {directory.__dict__}")
        self.selected_dir = directory
        for folder_tile in self.dir_list:
            if folder_tile == self.selected_dir:
                folder_tile.tile.content.bgcolor = crypt_drive_blue_medium_light
                folder_tile.tile.on_click = self.selected_dir_on_click_method
                self.subtitle.value = f"Selected folder: {self.selected_dir.path + self.selected_dir.name}"
            else:
                folder_tile.tile.content.bgcolor = crypt_drive_blue_semilight
                folder_tile.tile.on_click = lambda e, folder_tile_instance=folder_tile: self._update_selected_dir(folder_tile_instance)
        if self.alert.page:
            self.alert.update()

    def get_selected_directory_path_for_dialogs(self):
        """
        Get the full path of the selected directory for dialog operations.

        This method determines the path of the selected directory based on its
        relationship with the current directory and formats it appropriately
        to be used in dialog operations.

        :return: Full path of the selected directory.
        :rtype: str
        """
        logging.info(f"RETURNING SELECTED DIR: {self.selected_dir.__dict__}")
        if self.selected_dir == self.current_dir:
            trt = self.selected_dir.path if self.selected_dir.path == "/" else self.selected_dir.path[:-1] if self.selected_dir.path[-1] == "/" else self.selected_dir.path
        else:
            trt = self.selected_dir.path + self.selected_dir.name
        logging.info(f"TO RETURN STRING: {trt}")
        return trt

    def get_selected_directory_path_for_comms(self):
        """
        Constructs and returns the full path of the selected directory by combining its path
        and name attributes.

        The function utilizes logging to log the internal state of the selected directory
        and the resulting path string being returned.

        :return: The full concatenated path of the selected directory.
        :rtype: str
        """
        logging.info(f"RETURNING SELECTED DIR: {self.selected_dir.__dict__}")
        trt = self.selected_dir.path + self.selected_dir.name
        logging.info(f"TO RETURN STRING: {trt}")
        return trt




class AboutLine:
    """
    Represents a UI component that displays a line with an icon, two text elements,
    and an optional trailing button.

    This class is designed to create a structured user interface element that combines
    an icon, two lines of text, and an optional trailing button within a styled container.

    :ivar line: The container that holds the line's components, including the icon, text,
        and optional trailing button.
    :type line: ft.Container
    """
    def __init__(self, icon: ft.Icons, line_1: str, line_2: str, trailing_button: ft.IconButton = ft.Container()):
        """
        Initializes an instance of the class with the given parameters for creating a
        styled row container with an icon, two lines of text, and an optional trailing
        button. The class configures the container's layout, background color, padding,
        and border radius.

        :param icon: The icon to display in the container.
        :type icon: ft.Icons
        :param line_1: The first line of text to display in the container.
        :type line_1: str
        :param line_2: The second line of text to display in the container.
        :type line_2: str
        :param trailing_button: An optional trailing button to display in the container.
        :type trailing_button: ft.IconButton
        """
        self.line = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon),
                    ft.Column(
                        controls=[
                            ft.Text(value=line_1, font_family="Aeonik Bold", size=16),
                            ft.Text(value=line_2, font_family="Aeonik", size=16)
                        ],
                        spacing=2,
                        expand=True
                    ),
                    trailing_button
                ],
                expand=True,
            ),
            bgcolor=crypt_drive_blue_semilight,
            border_radius=15,
            padding=ft.padding.all(13),
        )
