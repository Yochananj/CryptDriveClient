"""
Displays versioning and dependency information for the CryptDrive application.

This module provides classes to create UI components specifically tailored for
displaying detailed version information about the CryptDrive application and
its dependencies. It is primarily built for use with the Flet framework and
is designed to display this information dynamically using animated transitions.
"""

import sys

import argon2
import cryptography
import flet as ft

from Dependencies.Constants import crypt_drive_blue, title_size, crypt_drive_blue_semilight


class AboutContainer:
    """
    Represents a container that displays information about CryptDrive.

    The class provides a structured way to display different pieces of
    versioning and library dependency information necessary for CryptDrive.
    This includes application-specific details, as well as version information
    for dependencies used within the application. The formatted lines of
    information are displayed dynamically within an animated container.

    :ivar title: The title text for the "About CryptDrive" section.
    :type title: ft.Text
    :ivar crypt_drive_version: A line displaying the version of CryptDrive.
    :type crypt_drive_version: ft.Control
    :ivar python_version: A line displaying the version of Python being used.
    :type python_version: ft.Control
    :ivar flet_version: A line displaying the version of the Flet library.
    :type flet_version: ft.Control
    :ivar cryptography_version: A line displaying the version of the Cryptography library being used.
    :type cryptography_version: ft.Control
    :ivar argon2_version: A line displaying the version of the Argon2 library being used.
    :type argon2_version: ft.Control
    :ivar about_lines: A collection of all version information lines to be displayed in the container.
    :type about_lines: list[ft.Control]
    :ivar about_column: A column container for holding the controls that display the versioning information.
    :type about_column: ft.Column
    :ivar animator: An animated switcher control that provides a fade-in/fade-out transition for displaying the column content dynamically.
    :type animator: ft.AnimatedSwitcher
    :ivar column: The main column that organizes the title and the animated content switcher for display.
    :type column: ft.Column
    """
    def __init__(self):
        """
        Class for displaying information about the CryptDrive application.

        This class initializes and organizes UI components to display details about the CryptDrive
        application, including the versions of CryptDrive and its dependencies. It is designed to
        work with the Flet framework and provides an animated display of the information.
        """
        self.title = ft.Text(value="About CryptDrive", font_family="Aeonik Black", size=title_size, color=crypt_drive_blue)

        self.crypt_drive_version = AboutLine(ft.Icons.INFO_OUTLINE, "CryptDrive Version:", "0.1.0", trailing_button=ft.IconButton(icon=ft.Icons.OPEN_IN_BROWSER_ROUNDED, url="https://github.com/yochananj/cryptdriveclient", tooltip="See GitHub Page")).line
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
    """
    Represents a UI component that displays a line with an icon, two text elements,
    and an optional trailing button.

    This class is designed to create a structured user interface element that combines
    an icon, two lines of text, and an optional trailing button within a styled container.

    :ivar line: The container that holds the line's components, including the icon, text,
        and optional trailing button.
    :type line: ft.Container
    """
    def __init__(self, icon: ft.Icons, line_1: str, line_2: str, trailing_button: ft.IconButton = ft.IconButton()):
        """
        Initializes an instance of the class with the given parameters for creating a
        styled row container with an icon, two lines of text, and an optional trailing
        button. The class configures the container's layout, background color, padding,
        and border radius.

        :param icon: The icon to display in the container.
        :type icon: ft.Icons
        :param line_1: The first line of text to display in the container.
        :type line_1: str
        :param line_2: The second line of text to display in the container.
        :type line_2: str
        :param trailing_button: An optional trailing button to display in the container.
        :type trailing_button: ft.IconButton
        """
        self.line = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon),
                    ft.Column(
                        controls=[
                            ft.Text(value=line_1, font_family="Aeonik Bold", size=16),
                            ft.Text(value=line_2, font_family="Aeonik", size=16)
                        ],
                        spacing=2,
                        expand=True
                    ),
                    trailing_button
                ],
                expand=True,
            ),
            bgcolor=crypt_drive_blue_semilight,
            border_radius=15,
            padding=ft.padding.all(13),
        )