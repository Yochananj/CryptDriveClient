import flet as ft

from Dependencies.Constants import crypt_drive_purple


class LoginView:
    """
    Represents the login view in the application.

    This class builds a user interface for logging in, including fields for username and password,
    a login button, and an option to switch to the sign-up view.

    :ivar logo: Display logo for the login view.
    :type logo: ft.Row
    :ivar username: Input field for the username.
    :type username: ft.TextField
    :ivar password: Input field for the password, secured with an option to reveal the text.
    :type password: ft.TextField
    :ivar log_in_button: Button to initiate the login process.
    :type log_in_button: ft.ElevatedButton
    :ivar switch_to_sign_up_button: Button to switch to the sign-up interface.
    :type switch_to_sign_up_button: ft.ElevatedButton
    """
    def __init__(self, username_start_value: str = "", password_start_value: str = ""):
        """
        Initializes a user interface component for login functionality, comprising a logo,
        username, and password input fields, as well as buttons for logging in or switching
        to a sign-up interface.

        :param username_start_value: Initial value for the username input field.
        :type username_start_value: str
        :param password_start_value: Initial value for the password input field.
        :type password_start_value: str
        """
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

    def build(self):
        """
        Constructs and returns a user interface (UI) view for the login screen. The view includes
        components such as a logo, username field, password field, a login button, and a
        button to switch to the sign-up screen. The layout is structured with a row and column
        arrangement, and all elements are centered both horizontally and vertically.

        :return: A user interface view for the login screen.
        :rtype: ft.View
        """
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
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )


