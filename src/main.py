"""
Manages the graphical user interface (GUI) and app execution entry point for
the CryptDrive application.

This module initializes the application, sets up the main GUI framework with
themes, navigation, and services, and launches the application.
"""

import logging
import platform

import flet as ft

from Controllers.HomeController import HomeController
from Controllers.LoginController import LoginController
from Controllers.SignUpController import SignUpController
from Dependencies.Constants import crypt_drive_fonts, crypt_drive_theme
from Services.ClientCommsManager import ClientCommsManager
from Services.FileEncryptionService import FileEncryptionService
from Services.PasswordsService import PasswordsService
from Views.HomeView import HomeView
from Views.LoginView import LoginView
from Views.SignUpView import SignUpView
from Views.UIElements import error_alert
from Views.ViewsAndRoutesList import ViewsAndRoutesList


class GUI:
    """
    Manages the graphical user interface (GUI) of the CryptDrive application.

    The GUI class is responsible for initializing the main page properties, setting up
    the theme, fonts, and window properties, and navigating between different views.
    It serves as the entry point for managing and switching between the different views
    and controllers in the application.

    :ivar top_view: The currently active view in the application.
    :type top_view: Optional[ft.UserControl]
    :ivar controller: The controller associated with the current view.
    :type controller: Optional[ft.BaseController]
    :ivar comms_manager: Manages communication with the server.
    :type comms_manager: ClientCommsManager
    :ivar file_encryption_service: Provides encryption and decryption services for files.
    :type file_encryption_service: FileEncryptionService
    :ivar passwords_service: Manages operations related to user passwords.
    :type passwords_service: PasswordsService
    :ivar page: Represents the main page of the GUI.
    :type page: ft.Page
    """
    def __init__(self, page: ft.Page):
        """
        Initializes the main application window and services.

        The class constructor sets up the main application window with specific
        dimensions, alignment preferences, and styles. It also initializes the
        required services, such as file management, communication, and encryption
        services, for the application to function. Additionally, the constructor
        handles platform-specific settings and navigates to the initial view.

        :param page: The application page object that represents the main window.
        :type page: ft.Page
        """
        self.top_view = None
        self.controller = None
        self.comms_manager = ClientCommsManager(self.navigator)
        self.file_encryption_service = FileEncryptionService()
        self.passwords_service = PasswordsService(self.file_encryption_service)

        self.page = page
        self.page.window.icon = "window_icon.ico"
        self.page.window.width = 1000
        self.page.window.min_width = 900
        self.page.window.height = 600
        self.page.window.min_height = 600
        self.page.window.center()
        self.page.scroll = True

        self.page.fonts = crypt_drive_fonts
        self.page.theme = crypt_drive_theme

        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.theme_mode = "light"
        if platform.system() == "Darwin": self.page.window.title_bar_hidden = True
        self.navigator(ViewsAndRoutesList.LOG_IN)


    def navigator(self, to_page: ViewsAndRoutesList, username: str = None, password: str = None):
        """
        Navigates to the specified view or route within the application's interface. Depending on the
        destination, it initializes the required page components, updates the display, and creates the
        appropriate controller to handle user interactions for that view. The navigation process manages
        situations such as login timeouts and ensures the correct theme and components are displayed for
        each view.

        :param to_page: The target view or route to navigate to. It must be an instance of the
            ViewsAndRoutesList enumeration.
        :param username: Optional; The username to pre-fill fields in views requiring user credentials,
            such as the login or sign-up pages.
        :param password: Optional; The password to pre-fill fields in views requiring user credentials,
            such as the login or sign-up pages.
        :return: None
        """
        logging.info(f"Navigating to {to_page}")
        self.page.clean()

        match to_page:
            case ViewsAndRoutesList.LOG_IN:
                timed_out = False
                if self.comms_manager.access_token == "timed_out": timed_out = True

                self.page.title = "CryptDrive: Log In"
                self.page.views.clear()
                self.top_view = LoginView(username_start_value=username, password_start_value=password)
                self.page.theme= crypt_drive_theme
                self.page.views.append(self.top_view.build())
                self.controller = LoginController(
                    page=self.page,
                    view=self.top_view,
                    navigator=self.navigator,
                    comms_manager=self.comms_manager,
                    file_encryption_service=self.file_encryption_service,
                    passwords_service=self.passwords_service
                )

                if timed_out: self.page.open(error_alert("Your log in timed out. Please log in again."))
            case ViewsAndRoutesList.SIGN_UP:
                self.page.title = "CryptDrive: Sign Up"
                self.page.views.clear()
                self.top_view = SignUpView(username_start_value=username, password_start_value=password)
                self.page.theme= crypt_drive_theme
                self.page.views.append(self.top_view.build())
                self.controller = SignUpController(
                    page=self.page,
                    view=self.top_view,
                    navigator=self.navigator,
                    comms_manager=self.comms_manager,
                    file_encryption_service=self.file_encryption_service,
                    passwords_service=self.passwords_service

                )
            case ViewsAndRoutesList.HOME:
                self.page.title = "CryptDrive: Home - Files"
                self.page.views.clear()
                self.top_view = HomeView(self.page.window.height, self.page.window.width)
                self.page.views.append(self.top_view.build())
                self.controller = HomeController(
                    page=self.page,
                    view=self.top_view,
                    navigator=self.navigator,
                    comms_manager=self.comms_manager,
                    file_encryption_service=self.file_encryption_service,
                    username=self.controller.view.username.value,
                    passwords_service=self.passwords_service
                )

        self.page.update()

if __name__ == "__main__":
    """
    Runs the application.
    """

    logging.basicConfig(level=logging.INFO)
    ft.app(GUI, assets_dir="../assets")




