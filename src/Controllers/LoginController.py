"""
Handles user login and authentication operations along with related UI interactions.

This module manages user login processes, including input validation, interaction with
the communication manager for authentication, and secure handling of encryption keys.
It bridges the UI components from the LoginView with backend login functionality, ensuring
user inputs are validated and appropriate navigation actions are taken based on login success
or failure.
"""


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
    """
    Handles user login-related interactions and operations within the application.

    The LoginController links the LoginView, navigation mechanisms, and essential
    services to manage user authentication. It ensures proper validation, feedback,
    and redirection based on user actions during the login process.

    :ivar view: The LoginView instance that renders and manages the UI components
        of the login page.
    :type view: LoginView
    :ivar navigator: The service responsible for navigating between application
        views/pages.
    :ivar comms_manager: The communication manager that facilitates interactions,
        potentially with an external service, to authenticate users.
    :ivar file_encryption_service: Manages encryption operations, specifically
        deriving, storing, and managing file encryption keys securely.
    :type file_encryption_service: FileEncryptionService
    :ivar passwords_service: Manages password-related functionalities, such as
        hashing and validation.
    :type passwords_service: PasswordsService
    """
    def __init__(self, page: ft.Page, view: LoginView, navigator, comms_manager, file_encryption_service: FileEncryptionService, passwords_service: PasswordsService):
        """
        Initializes an instance of the class and sets up necessary dependencies and
        handlers.

        :param page: An instance of flet's Page used to interact with the UI.
        :type page: ft.Page
        :param view: The LoginView instance used to manage and render the login view.
        :type view: LoginView
        :param navigator: Service or utility responsible for navigation between
            application views/pages.
        :param comms_manager: The communication manager responsible for handling
            communication, potentially with an external service.
        :param file_encryption_service: The FileEncryptionService instance that
            handles file encryption operations.
        :type file_encryption_service: FileEncryptionService
        :param passwords_service: The PasswordsService instance that manages
            password-related functionalities and operations.
        :type passwords_service: PasswordsService
        """
        self.view = view
        self.navigator = navigator
        self.comms_manager = comms_manager
        self.file_encryption_service = file_encryption_service
        self.passwords_service = passwords_service

        self._upon_text_field_change(page)
        self._attach_handlers(page)

    def _attach_handlers(self, page: ft.Page):
        """
        Attaches event handlers to UI components within the provided page. These handlers respond
        to specific user interactions such as text field changes and button clicks.

        :param page: The page instance to which the event handlers will be attached.
        :type page: ft.Page
        :return: None
        """
        """
        
        :param page: 
        :return: 
        """
        self.view.username.on_change = lambda e: self._upon_text_field_change(page)
        self.view.password.on_change = lambda e: self._upon_text_field_change(page)
        self.view.log_in_button.on_click = lambda e: self._upon_log_in_click(page)
        self.view.switch_to_sign_up_button.on_click = lambda e: self._upon_switch_to_sign_up_click(page)

    def _upon_text_field_change(self, page: ft.Page):
        """
        Handles updates to the state of the text fields and enables or disables the login
        button based on whether the username and password fields are populated.

        :param page: The current Page instance, used for updating the UI state.
        :type page: ft.Page
        """
        if self.view.username.value and self.view.password.value:
            self.view.log_in_button.disabled = False
        else:
            self.view.log_in_button.disabled = True
        page.update()


    def _upon_switch_to_sign_up_click(self, page: ft.Page):
        """
        Handles the event triggered upon clicking the "Switch to Sign Up" button. It gathers the current username and password
        values, navigates to the sign-up view, and updates the page.

        :param page: The current page instance, which is updated after navigation
        :type page: ft.Page
        """
        current_entry_username, current_entry_password = "", ""
        if self.view.username.value: current_entry_username = self.view.username.value
        if self.view.password.value: current_entry_password = self.view.password.value
        self.navigator(ViewsAndRoutesList.SIGN_UP, username=current_entry_username, password=current_entry_password)
        page.update()

    def _upon_log_in_click(self, page: ft.Page):
        """
        Handles the log-in button click event by validating input, hashing the password, sending login credentials
        to the server, and securely handling session keys upon successful authentication.

        :param page: An ft.Page object representing the current app page where navigation and events occur.

        :raises ValueError: If the username is not between 3 and 32 characters long.
        :raises ValueError: If the password is not between 8 and 64 characters long.

        :return: None
        """
        logging.info("Log In clicked")

        username, password = self.view.username.value.lower().strip(), self.view.password.value

        if " " in username:
            page.open(error_alert("Username cannot contain spaces."))
            page.update()
            return

        if len(username) < 3 or len(username) > 32:
            page.open(error_alert("Username must be between 3 and 32 characters long."))
            page.update()
            return
        if len(password) < 8 or len(password) > 64:
            page.open(error_alert("Password must be between 8 and 64 characters long."))
            page.update()
            return


        status, response_data = self.comms_manager.send_message(verb=Verbs.LOG_IN, data=[username, password])
        if status == "SUCCESS":
            user_data = json.loads(response_data)
            salt = b64decode(user_data["salt"].encode())
            encrypted_file_master_key = b64decode(user_data["encrypted_file_master_key"].encode())
            nonce = b64decode(user_data["nonce"].encode())

            logging.info(f"Salt: {salt} \n Encrypted File Master Key: {encrypted_file_master_key} \n Nonce: {nonce}")

            self.file_encryption_service.derive_and_store_derived_key_from_password_and_salt(password, salt)
            self.file_encryption_service.store_encrypted_master_key_and_nonce(encrypted_file_master_key, nonce)

            self.navigator(ViewsAndRoutesList.HOME)
        else:
            logging.info("Log In failed:")
            page.open(error_alert("Log In Failed: Check Username and Password"))
            page.update()