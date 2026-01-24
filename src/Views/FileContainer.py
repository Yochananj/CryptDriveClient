import flet as ft

from Dependencies.Constants import crypt_drive_blue_semilight, crypt_drive_purple, crypt_drive_blue, title_size
from Views.UIElements import FolderTile, FileTile


class FileContainer:
    def __init__(self):
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
