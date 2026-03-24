"""
Defines the user interface for the sign-up page.

This module provides the SignUpView class, which encapsulates the sign-up
page's structure, components, and behavior, allowing users to create an
account by entering their details. The interface includes a logo, input
fields for credentials, and buttons for actions such as signing up or
navigating to the log-in page.
"""


import flet as ft

from Dependencies.Constants import crypt_drive_purple


class SignUpView:
    """
    Represents the sign-up view of the application.

    This class serves as the user interface for the sign-up functionality, including input fields for
    username, password, and password confirmation. It also provides action buttons for signing up
    and switching to the log-in view. The view is designed for alignment and usability, including an
    app logo for branding purposes.

    :ivar logo: A UI component representing the application logo.
    :type logo: ft.Row
    :ivar username: A text field for entering the username.
    :type username: ft.TextField
    :ivar password: A text field for entering the password.
    :type password: ft.TextField
    :ivar password_confirmation: A text field for confirming the password.
    :type password_confirmation: ft.TextField
    :ivar sign_up_button: A button to initiate the sign-up process.
    :type sign_up_button: ft.ElevatedButton
    :ivar switch_to_log_in_button: A button to switch to the log-in view.
    :type switch_to_log_in_button: ft.ElevatedButton
    """
    def __init__(self, username_start_value: str = "", password_start_value: str = ""):
        """
        Initializes the signup form with configurable username and password default values.

        :param username_start_value: Initial value for the username field.
        :param password_start_value: Initial value for the password field.
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
        self.username = ft.TextField(value=username_start_value, label="Username", width=300, autofocus=True, prefix_icon=ft.Icon(ft.Icons.PERSON_ROUNDED, color=crypt_drive_purple))

        self.password = ft.TextField(value=password_start_value, label="Password", text_vertical_align=ft.VerticalAlignment.START, width=300, password=True, prefix_icon=ft.Icon(ft.Icons.KEY_ROUNDED, color=crypt_drive_purple), can_reveal_password=True)

        self.password_confirmation = ft.TextField(label="Confirm Password", text_vertical_align=ft.VerticalAlignment.START, width=300, password=True, prefix_icon=ft.Icon(ft.Icons.KEY_ROUNDED, color=crypt_drive_purple), can_reveal_password=True)

        self.sign_up_button = ft.ElevatedButton(text="Sign Up", width=300, disabled=True)

        self.switch_to_log_in_button = ft.ElevatedButton(text="Log In Instead", width=300, disabled=False)


    def build(self):
        """
        Constructs and returns a sign-up page view with a specific route and layout.

        This method builds the user interface for the sign-up page, organizing its
        elements in a structure composed of rows and columns. The view includes
        controls for user authentication and navigation.

        :return: A flet View object representing the sign-up page.
        :rtype: ft.View
        """
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
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )


