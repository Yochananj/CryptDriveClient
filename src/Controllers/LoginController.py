import logging

import flet as ft

from Views.LoginView import LoginView
from Views.UIElements import error_alert
from Views.ViewsAndRoutesList import ViewsAndRoutesList
from Services.PasswordHashingService import PasswordHashingService
from Dependencies.Constants import crypt_drive_theme
from Dependencies.VerbDictionary import Verbs


class LoginController:
    def __init__(self, page: ft.Page, view: LoginView, navigator, comms_manager):
        self.view = view
        self.navigator = navigator
        self.upon_text_field_change(page)
        self.comms_manager = comms_manager
        page.theme = crypt_drive_theme
        self.attach_handlers(page)

    def attach_handlers(self, page: ft.Page):
        self.view.username.on_change = lambda e: self.upon_text_field_change(page)
        self.view.password.on_change = lambda e: self.upon_text_field_change(page)
        self.view.log_in_button.on_click = lambda e: self.upon_log_in_click(page)
        self.view.switch_to_sign_up_button.on_click = lambda e: self.upon_switch_to_sign_up_click(page)

    def upon_text_field_change(self, page: ft.Page):
        if self.view.username.value and self.view.password.value:
            self.view.log_in_button.disabled = False
        else:
            self.view.log_in_button.disabled = True
        page.update()


    def upon_switch_to_sign_up_click(self, page: ft.Page):
        current_entry_username, current_entry_password = "", ""
        if self.view.username.value: current_entry_username = self.view.username.value
        if self.view.password.value: current_entry_password = self.view.password.value
        self.navigator(ViewsAndRoutesList.SIGN_UP, username=current_entry_username, password=current_entry_password)
        page.update()

    def upon_log_in_click(self, page: ft.Page):
        logging.debug("Log In clicked")
        if len(self.view.username.value) < 3 or len(self.view.username.value) > 32:
            page.open(error_alert("Username must be between 3 and 32 characters long."))
            page.update()
            return
        if len(self.view.password.value) < 8 or len(self.view.password.value) > 64:
            page.open(error_alert("Password must be between 8 and 64 characters long."))
            page.update()
            return
        status, error = self.comms_manager.send_message(verb=Verbs.LOG_IN, data=[self.view.username.value, PasswordHashingService.hash(self.view.password.value)])
        if status == "SUCCESS":
            self.navigator(ViewsAndRoutesList.HOME)
        else:
            logging.debug("Log In failed:")
            page.open(self.view.log_in_failed_snack_bar)
            page.update()