import logging
import os
import platform

import flet as ft
from flet.core.types import AppView

from Services.ClientFileService import ClientFileService
from Services.ClientCommsManager import ClientCommsManager

from Controllers.HomeController import HomeController
from Controllers.LoginController import LoginController
from Controllers.SignUpController import SignUpController
from Services.FileEncryptionService import FileEncryptionService
from Services.PasswordsService import PasswordsService

from Views.UIElements import error_alert
from Views.HomeView import HomeView
from Views.LoginView import LoginView
from Views.SignUpView import SignUpView
from Views.ViewsAndRoutesList import ViewsAndRoutesList
from Dependencies.Constants import crypt_drive_fonts, crypt_drive_theme


class GUI:
    def __init__(self, page: ft.Page):
        self.top_view = None
        self.controller = None
        self.comms_manager = ClientCommsManager()
        self.file_service = ClientFileService()
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
        logging.info(f"Navigating to {to_page}")
        self.page.clean()

        match to_page:
            case ViewsAndRoutesList.LOG_IN:
                timed_out = False
                if self.comms_manager.login_token != "no_token": timed_out = True

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

                if timed_out: self.page.open(error_alert("Your Log In timed out. Please log in again."))
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
                    client_file_service=self.file_service,
                    file_encryption_service=self.file_encryption_service,
                    username=self.controller.view.username.value,
                    passwords_service=self.passwords_service
                )

        self.page.update()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info(f"{os.path.dirname(__file__)}/assets/window_icon.ico")
    ft.app(GUI, assets_dir="../assets")




