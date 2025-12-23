import flet as ft

from Dependencies.Constants import crypt_drive_blue


class SettingsContainer:
    def __init__(self):
        self.title = ft.Text(value="Your Settings", font_family="Aeonik Black", size=90, color=crypt_drive_blue)

        self.column = ft.Column(
            controls=[
                self.title,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    def build(self):
        return self.column