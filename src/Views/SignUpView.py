import flet as ft

from Dependencies.Constants import crypt_drive_purple
from Views.UIElements import error_alert


class SignUpView:
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
        self.username = ft.TextField(value=username_start_value, label="Username", width=300, autofocus=True, prefix_icon=ft.Icon(ft.Icons.PERSON_ROUNDED, color=crypt_drive_purple))

        self.password = ft.TextField(value=password_start_value, label="Password", text_vertical_align=ft.VerticalAlignment.START, width=300, password=True, prefix_icon=ft.Icon(ft.Icons.KEY_ROUNDED, color=crypt_drive_purple), can_reveal_password=True)

        self.password_confirmation = ft.TextField(label="Confirm Password", text_vertical_align=ft.VerticalAlignment.START, width=300, password=True, prefix_icon=ft.Icon(ft.Icons.KEY_ROUNDED, color=crypt_drive_purple), can_reveal_password=True)

        self.sign_up_button = ft.ElevatedButton(text="Sign Up", width=300, disabled=True)

        self.switch_to_log_in_button = ft.ElevatedButton(text="Log In Instead", width=300, disabled=False)

        self.taken_username_snack_bar = error_alert("Sign Up Failed: Username is already taken.")

        self.passwords_must_match_snack_bar = error_alert("Password and Password Confirmation must be identical.")

        self.username_length_snack_bar = error_alert("Username must be between 3 and 32 characters long.")

        self.password_length_snack_bar = error_alert("Password must be between 8 and 64 characters long.")


    def build(self):
        return ft.View(
            route = "/sign_up",
            controls=[ft.Row(
                controls=[
                    ft.Column([
                        self.logo,
                        self.username,
                        self.password,
                        self.password_confirmation,
                        self.sign_up_button,
                        self.switch_to_log_in_button]
                    )],
                alignment=ft.MainAxisAlignment.CENTER)],
            can_pop=False,
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )


