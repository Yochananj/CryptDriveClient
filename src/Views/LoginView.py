import flet as ft

from Views.UIElements import error_alert
from Dependencies.Constants import crypt_drive_purple


class LoginView:
    def __init__(self, username_start_value: str = "", password_start_value: str = ""):
        self.logo = ft.Row(
            controls=[
                ft.Column(width=30, controls=[ft.Text("")]),
                ft.Image(
                    src="icon.png",
                    width=200,
                    height=200,
                    fit=ft.ImageFit.FIT_WIDTH
                )]
        )
        self.username = ft.TextField(value=username_start_value, label="Username", width=300, autofocus=True, prefix_icon=ft.Icon(ft.Icons.PERSON_ROUNDED, color=crypt_drive_purple), max_lines=1)
        self.password = ft.TextField(value=password_start_value, label="Password", width=300, text_vertical_align=ft.VerticalAlignment.START, password=True, prefix_icon=ft.Icon(ft.Icons.KEY_ROUNDED, color=crypt_drive_purple), can_reveal_password=True)
        self.log_in_button = ft.ElevatedButton(text="Log In", width=300, disabled=True)
        self.switch_to_sign_up_button = ft.ElevatedButton(text="Sign Up Instead", width=300, disabled=False)
        self.log_in_failed_snack_bar = error_alert("Log In Failed: Check Username and Password")

    def build(self):
        return ft.View(
            route = "/log_in",
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            [
                            self.logo,
                            self.username,
                            self.password,
                            self.log_in_button,
                            self.switch_to_sign_up_button
                            ]
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            can_pop=False,
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )


