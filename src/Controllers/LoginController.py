import json
import logging
from base64 import b64decode

import flet as ft

from Dependencies.VerbDictionary import Verbs
from Services.FileEncryptionService import FileEncryptionService
from Services.PasswordsService import PasswordsService
from Views.LoginView import LoginView
from Views.UIElements import error_alert
from Views.ViewsAndRoutesList import ViewsAndRoutesList


class LoginController:
    def __init__(self, page: ft.Page, view: LoginView, navigator, comms_manager, file_encryption_service: FileEncryptionService, passwords_service: PasswordsService):
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
        self.view.log_in_button.on_click = lambda e: self._upon_log_in_click(page)
        self.view.switch_to_sign_up_button.on_click = lambda e: self._upon_switch_to_sign_up_click(page)

    def _upon_text_field_change(self, page: ft.Page):
        if self.view.username.value and self.view.password.value:
            self.view.log_in_button.disabled = False
        else:
            self.view.log_in_button.disabled = True
        page.update()


    def _upon_switch_to_sign_up_click(self, page: ft.Page):
        current_entry_username, current_entry_password = "", ""
        if self.view.username.value: current_entry_username = self.view.username.value
        if self.view.password.value: current_entry_password = self.view.password.value
        self.navigator(ViewsAndRoutesList.SIGN_UP, username=current_entry_username, password=current_entry_password)
        page.update()

    def _upon_log_in_click(self, page: ft.Page):
        logging.info("Log In clicked")
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

        status, response_data = self.comms_manager.send_message(verb=Verbs.LOG_IN, data=[username, password_hash])
        if status == "SUCCESS":
            user_data = json.loads(response_data)
            salt = b64decode(user_data["salt"].encode())
            encrypted_file_master_key = b64decode(user_data["encrypted_file_master_key"].encode())
            nonce = b64decode(user_data["nonce"].encode())

            logging.critical(f"Salt: {salt} \n Encrypted File Master Key: {encrypted_file_master_key} \n Nonce: {nonce}")

            self.file_encryption_service.derive_and_store_derived_key_from_password_and_salt(password, salt)
            self.file_encryption_service.store_encrypted_master_key_and_nonce(encrypted_file_master_key, nonce)

            self.navigator(ViewsAndRoutesList.HOME)
        else:
            logging.info("Log In failed:")
            page.open(error_alert("Log In Failed: Check Username and Password"))
            page.update()