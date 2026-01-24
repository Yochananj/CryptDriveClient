import logging
from os import urandom

import flet as ft

from Dependencies.VerbDictionary import Verbs
from Services.ClientCommsManager import ClientCommsManager
from Services.FileEncryptionService import FileEncryptionService
from Services.PasswordsService import PasswordsService
from Views.UIElements import error_alert
from Views.ViewsAndRoutesList import ViewsAndRoutesList


class SignUpController:
    def __init__(self, page: ft.Page, view, navigator, comms_manager: ClientCommsManager, file_encryption_service: FileEncryptionService, passwords_service: PasswordsService):
        self.view = view
        self.navigator = navigator
        self.comms_manager = comms_manager
        self.file_encryption_service = file_encryption_service
        self.passwords_service = passwords_service

        self._upon_text_field_change(page)
        self._attach_handlers(page)

    def _attach_handlers(self, page: ft.Page):
        self.view.username.on_change = lambda e: self._upon_text_field_change(page)
        self.view.password.on_change = lambda e: self._upon_text_field_change(page)
        self.view.password_confirmation.on_change = lambda e: self._upon_text_field_change(page)
        self.view.sign_up_button.on_click = lambda e: self._upon_sign_up_click(page)
        self.view.switch_to_log_in_button.on_click = lambda e: self._upon_switch_to_log_in_click(page)


    def _upon_text_field_change(self, page: ft.Page):
        if self.view.username.value and self.view.password.value and self.view.password_confirmation.value:
            self.view.sign_up_button.disabled = False
        else:
            self.view.sign_up_button.disabled = True
        page.update()


    def _upon_switch_to_log_in_click(self, page: ft.Page):
        current_entry_username = ""
        current_entry_password = ""
        if self.view.username.value: current_entry_username = self.view.username.value
        if self.view.password.value: current_entry_password = self.view.password.value
        self.navigator(ViewsAndRoutesList.LOG_IN, username=current_entry_username, password=current_entry_password)
        page.update()

    def _upon_sign_up_click(self, page: ft.Page):
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

        username, password = self.view.username.value, self.view.password.value

        password_hash = PasswordsService.hash_password(password)

        salt, encrypted_file_master_key, nonce = self.file_encryption_service.create_new_encryption_credentials_from_password(password, new_file_master_key=True)

        logging.critical(f"Salt: {salt} \n Encrypted File Master Key: {encrypted_file_master_key} \n Nonce: {nonce}")

        status, response_data = self.comms_manager.send_message(Verbs.SIGN_UP, [username, password_hash, salt, encrypted_file_master_key, nonce])
        if status == "SUCCESS":
            self.navigator(ViewsAndRoutesList.HOME)
        else:
            logging.debug("Log In failed:")
            page.open(error_alert("Sign Up Failed: Username is already taken."))
            page.update()