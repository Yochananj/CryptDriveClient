import flet as ft

from Dependencies.Constants import crypt_drive_blue, crypt_drive_blue_semilight, crypt_drive_purple, title_size


class AccountContainer:
    """
    Represents a UI container for account management functionality.

    This class is responsible for displaying and managing the account details
    and related actions, including changing the username, changing the password,
    and logging out. It organizes these elements into structured layouts and
    provides an animated transition for updates to the UI.

    :ivar title: The title of the account management section.
    :type title: ft.Text
    :ivar change_username_button: Button that allows users to request a username change.
    :type change_username_button: ft.FloatingActionButton
    :ivar change_password_button: Button that allows users to request a password change.
    :type change_password_button: ft.FloatingActionButton
    :ivar log_out_button: Button that allows users to log out of their account.
    :type log_out_button: ft.FloatingActionButton
    :ivar buttons: A list containing all account action buttons.
    :type buttons: list[ft.FloatingActionButton]
    :ivar username_row: A UI row displaying the current username details.
    :type username_row: ft.Row
    :ivar password_row: A UI row displaying the current password details as masked text.
    :type password_row: ft.Row
    :ivar account_details: A container that groups and displays account-related information.
    :type account_details: ft.Container
    :ivar column: A layout container holding the title, account details, and action buttons.
    :type column: ft.Column
    :ivar animator: An animated container for smooth and dynamic UI transitions.
    :type animator: ft.AnimatedSwitcher
    """
    def __init__(self, username: str):
        self.title = ft.Text(value="Your Account", font_family="Aeonik Black", size=title_size, color=crypt_drive_blue)

        self.change_username_button = ft.FloatingActionButton(icon=ft.Icons.MANAGE_ACCOUNTS_ROUNDED, text="Change Username",   bgcolor=crypt_drive_blue_semilight, elevation=0)
        self.change_password_button = ft.FloatingActionButton(icon=ft.Icons.KEY_ROUNDED, text="Change Password",  bgcolor=crypt_drive_blue_semilight, elevation=0)
        self.log_out_button = ft.FloatingActionButton(icon=ft.Icons.SWITCH_ACCOUNT, text="Log Out", bgcolor=crypt_drive_blue_semilight, elevation=0)

        self.buttons = [
            self.change_username_button,
            self.change_password_button,
            self.log_out_button
        ]

        self.username_row = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PERSON_ROUNDED, size=25, color=crypt_drive_purple),
                        ft.Column(
                            [
                                ft.Text("Username:", color=crypt_drive_purple),
                                ft.Text(username, color=crypt_drive_purple)
                            ],
                            spacing=2
                        )
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        )

        self.password_row = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.KEY_ROUNDED, size=25),
                        ft.Column(
                            controls=[
                                ft.Text("Password:", color=crypt_drive_purple),
                                ft.Text("********", color=crypt_drive_purple)
                            ],
                            spacing=2
                        )
                    ],
                    expand=True
                ),
            ],
            expand=True,
        )

        self.account_details = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE), ft.Text("Account Details", size=25, font_family="Aeonik Bold", color=crypt_drive_purple)
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            self.username_row,
                            self.password_row
                        ],
                    )
                ],
                expand=True
            ),
            bgcolor=crypt_drive_blue_semilight,
            border_radius=15,
            padding=ft.padding.all(15),
        )

        self.column = ft.Column(
            controls=[
                self.title,
                self.account_details,
                ft.Row([self.change_username_button, self.change_password_button, self.log_out_button]),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        self.animator = ft.AnimatedSwitcher(
            content=ft.Container(),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=300,
            switch_in_curve=ft.AnimationCurve.EASE_IN,
            switch_out_curve=ft.AnimationCurve.EASE_OUT,
        )
