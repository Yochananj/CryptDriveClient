import logging

import flet as ft
from Services.ClientCommsManager import ClientClass
from Views.UIElements import error_alert
from Views.ViewsAndRoutesList import ViewsAndRoutesList
from Services.PasswordHashingService import PasswordHashingService
from Dependencies.Constants import crypt_drive_theme
from Dependencies.VerbDictionary import Verbs


class SignUpController:
    def __init__(self, page: ft.Page, view, navigator, comms_manager: ClientClass):
        self.view = view
        self.navigator = navigator
        self.comms_manager = comms_manager
        self.upon_text_field_change(page)
        self.attach_handlers(page)
        page.theme = crypt_drive_theme

    def attach_handlers(self, page: ft.Page):
        self.view.username.on_change = lambda e: self.upon_text_field_change(page)
        self.view.password.on_change = lambda e: self.upon_text_field_change(page)
        self.view.password_confirmation.on_change = lambda e: self.upon_text_field_change(page)
        self.view.sign_up_button.on_click = lambda e: self.upon_sign_up_click(page)
        self.view.switch_to_log_in_button.on_click = lambda e: self.upon_switch_to_log_in_click(page)


    def upon_text_field_change(self, page: ft.Page):
        if self.view.username.value and self.view.password.value and self.view.password_confirmation.value:
            self.view.sign_up_button.disabled = False
        else:
            self.view.sign_up_button.disabled = True
        page.update()


    def upon_switch_to_log_in_click(self, page: ft.Page):
        current_entry_username = ""
        current_entry_password = ""
        if self.view.username.value: current_entry_username = self.view.username.value
        if self.view.password.value: current_entry_password = self.view.password.value
        self.navigator(ViewsAndRoutesList.LOG_IN, username=current_entry_username, password=current_entry_password)
        page.update()

    def upon_sign_up_click(self, page: ft.Page):
        logging.debug("Sign Up clicked")

        if self.view.password.value != self.view.password_confirmation.value:
            logging.debug("Passwords do not match.")
            page.open(error_alert("Password and Password Confirmation must be identical."))
            page.update()
            return

        if len(self.view.username.value) < 3 or len(self.view.username.value) > 32:
            page.open(error_alert("Username must be between 3 and 32 characters long."))
            page.update()
            return

        if len(self.view.password.value) < 8 or len(self.view.password.value) > 64:
            page.open(error_alert("Password must be between 8 and 64 characters long."))
            page.update()
            return

        status, error = self.comms_manager.send_message(Verbs.SIGN_UP, [self.view.username.value, PasswordHashingService.hash(self.view.password.value)])
        if status == "SUCCESS":
            self.navigator(ViewsAndRoutesList.HOME)
        else:
            logging.debug("Log In failed:")
            page.open(error_alert("Sign Up Failed: Username is already taken."))
            page.update()