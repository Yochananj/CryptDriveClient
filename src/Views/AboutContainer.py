import sys

import argon2
import cryptography
import flet as ft

from Dependencies.Constants import crypt_drive_blue, title_size, crypt_drive_blue_semilight


class AboutContainer:
    def __init__(self):
        self.title = ft.Text(value="About CryptDrive", font_family="Aeonik Black", size=title_size, color=crypt_drive_blue)

        self.crypt_drive_version = AboutLine(ft.Icons.INFO_OUTLINE, "CryptDrive Version:", "0.1.0").line
        self.python_version = AboutLine(ft.Icons.CODE_ROUNDED, "Python Version:", f"{sys.version}").line
        self.flet_version = AboutLine(ft.Icons.DESKTOP_WINDOWS, "Flet Version:", "0.28.3").line
        self.cryptography_version = AboutLine(ft.Icons.KEY_ROUNDED, "Cryptography Version:", f"{cryptography.__version__}").line
        self.argon2_version = AboutLine(ft.Icons.LOCK_ROUNDED, "Argon2 Version:", f"{argon2.__version__}").line

        self.about_lines = [
            self.crypt_drive_version,
            self.python_version,
            self.flet_version,
            self.cryptography_version,
            self.argon2_version
        ]

        self.about_column = ft.Column(
            controls=[]
        )

        self.animator = ft.AnimatedSwitcher(
            content=self.about_column,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=300,
            switch_in_curve=ft.AnimationCurve.EASE_IN,
            switch_out_curve=ft.AnimationCurve.EASE_OUT,
            expand=True,
        )

        self.column = ft.Column(
            controls=[
                self.title,
                self.animator
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )



class AboutLine:
    def __init__(self, icon: ft.Icons, line_1: str, line_2: str):
        self.line = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon),
                    ft.Column(
                        controls=[
                            ft.Text(value=line_1, font_family="Aeonik Bold", size=16),
                            ft.Text(value=line_2, font_family="Aeonik", size=16)
                        ],
                        spacing=2
                    ),
                ],
                expand=True,
            ),
            bgcolor=crypt_drive_blue_semilight,
            border_radius=15,
            padding=ft.padding.all(13),
        )