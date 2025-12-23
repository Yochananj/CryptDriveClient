import flet as ft

from Dependencies.Constants import crypt_drive_blue


class AccountContainer:
    def __init__(self):
        self.title = ft.Text(value="Your Account", font_family="Aeonik Black", size=90, color=crypt_drive_blue)
        self.username_row = ft.Row(controls=[ft.Text("Username:"), ft.TextField(value="", width=300,)])
        self.log_out_button = ft.Button(text="Log Out", width=300, icon=ft.Icons.SWITCH_ACCOUNT)

        self.column = ft.Column(
            controls=[
                self.title,
                self.log_out_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,

        )

    def build(self):
        return self.column