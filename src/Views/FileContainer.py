import flet as ft

from Dependencies.Constants import crypt_drive_blue_semilight, crypt_drive_purple, crypt_drive_blue, title_size
from Views.UIElements import FolderTile, FileTile


class FileContainer:
    """
    Represents a container for managing and displaying a collection of files and directories.

    This class is used as a visual and interactive component for managing files and directories
    within a user interface. It provides attributes for titles, buttons, and container structures
    to organize and display file and directory elements.

    :ivar title: The title displayed for the file container.
    :type title: ft.Text
    :ivar column: The primary column layout holding controls for file management.
    :type column: ft.Column
    :ivar tiles_column: The column used to align individual tiles for directories and files.
    :type tiles_column: ft.Column
    :ivar tiles_alignment_container: A container responsible for aligning and padding the tiles column.
    :type tiles_alignment_container: ft.Container
    :ivar animator: An animated switcher used to transition between different content views.
    :type animator: ft.AnimatedSwitcher
    :ivar current_directory: The currently active directory where files and subdirectories are being displayed.
    :type current_directory: FolderTile
    :ivar directories: A list of directory tiles representing all subdirectories in the current directory.
    :type directories: list[FolderTile]
    :ivar files: A list of file tiles representing all files in the current directory.
    :type files: list[FileTile]
    :ivar upload_file_button: A floating action button used for uploading new files.
    :type upload_file_button: ft.FloatingActionButton
    :ivar create_dir_button: A floating action button used for creating new directories.
    :type create_dir_button: ft.FloatingActionButton
    :ivar subtitle_row: A row layout used to display subtitles or additional controls.
    :type subtitle_row: ft.Row
    """
    def __init__(self):
        """
        Represents a user interface for managing files and directories, with controls for navigating,
        uploading files, and creating directories.
        """
        self.title = ft.Text(value="Your Files", font_family="Aeonik Black", size=title_size, color=crypt_drive_blue)

        self.column = ft.Column(
            controls=[],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            scroll=True
        )
        self.tiles_column = ft.Column(
            controls=[],
            alignment=ft.MainAxisAlignment.START,
            scroll=False,
            expand=True
        )

        self.tiles_alignment_container = ft.Container(
            content=self.tiles_column,
            alignment=ft.Alignment(0, -1),
            expand=True,
            padding=ft.padding.only(bottom=20)
        )

        self.animator = ft.AnimatedSwitcher(
            content=ft.Container(),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=300,
            switch_in_curve=ft.AnimationCurve.EASE_IN,
            switch_out_curve=ft.AnimationCurve.EASE_OUT,
            expand=True,
        )

        self.current_directory: FolderTile = None
        self.directories: list[FolderTile] = []
        self.files: list[FileTile] = []
        self.upload_file_button = ft.FloatingActionButton(
            content=ft.Icon(name=ft.Icons.FILE_UPLOAD_OUTLINED, color=crypt_drive_purple),
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=crypt_drive_blue_semilight,
            elevation=0,
            width=50,
            height=50,
        )
        self.create_dir_button = ft.FloatingActionButton(
            content=ft.Icon(name=ft.Icons.CREATE_NEW_FOLDER, color=crypt_drive_purple),
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=crypt_drive_blue_semilight,
            elevation=0,
            height=50,
            width=50,
        )
        self.subtitle_row = ft.Row(
            controls=[],
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand_loose=True
        )
