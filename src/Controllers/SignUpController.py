"""
Manages the user registration process, including validation, service interaction,
and navigation logic.
"""


import logging

import flet as ft

from Dependencies.VerbDictionary import Verbs
from Services.ClientCommsManager import ClientCommsManager
from Services.FileEncryptionService import FileEncryptionService
from Services.PasswordsService import PasswordsService
from Views.UIElements import error_alert
from Views.ViewsAndRoutesList import ViewsAndRoutesList


class SignUpController:
    """
    Manages the sign-up process, including handling user input, validating data,
    and interacting with relevant services for user registration.

    The `SignUpController` class is responsible for orchestrating the sign-up
    workflow. It attaches handlers to the UI components, validates user input,
    and communicates with backend services to register a new user. Additionally,
    it enables navigation to other views as required.

    :ivar view: Interface for accessing and manipulating the view's UI components.
    :type view: Any
    :ivar navigator: A callable for navigating between views and routes.
    :type navigator: Callable
    :ivar comms_manager: Handles communication with the backend server for user sign-up.
    :type comms_manager: ClientCommsManager
    :ivar file_encryption_service: Service for managing encryption-related operations.
    :type file_encryption_service: FileEncryptionService
    :ivar passwords_service: Service for password hashing and verification.
    :type passwords_service: PasswordsService
    """
    def __init__(self, page: ft.Page,
                 view,
                 navigator,
                 comms_manager: ClientCommsManager,
                 file_encryption_service: FileEncryptionService,
                 passwords_service: PasswordsService
                 ):
        """
        Initializes the class with required services and configurations.

        :param page: Represents the page object for UI interactions.
        :type page: ft.Page
        :param view: Encapsulates the view logic and presentation settings.
        :param navigator: Handles navigation between different app sections.
        :param comms_manager: Manages client-side communication with external services or
            backends.
        :type comms_manager: ClientCommsManager
        :param file_encryption_service: Provides functionality for file encryption and
            related cryptographic operations.
        :type file_encryption_service: FileEncryptionService
        :param passwords_service: Manages password-related operations, such as storage
            or validation.
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
        Attach event handlers to various view components.

        This method links UI events to their respective handler functions, ensuring
        that interactions with interface elements trigger the appropriate behavior.

        :param page: The page object representing the current UI frame and
            its components for which the event-processing need to be established.
        :type page: ft.Page
        """
        self.view.username.on_change = lambda e: self._upon_text_field_change(page)
        self.view.password.on_change = lambda e: self._upon_text_field_change(page)
        self.view.password_confirmation.on_change = lambda e: self._upon_text_field_change(page)
        self.view.sign_up_button.on_click = lambda e: self._upon_sign_up_click(page)
        self.view.switch_to_log_in_button.on_click = lambda e: self._upon_switch_to_log_in_click(page)


    def _upon_text_field_change(self, page: ft.Page):
        """
        Responds to changes in the text fields of the view and updates the state
        of the sign-up button. Enables the sign-up button if all required fields
        (username, password, and password confirmation) are filled; otherwise,
        disables the button.

        :param page: Represents the current page instance that needs to be updated.
        :type page: ft.Page
        """
        if self.view.username.value and self.view.password.value and self.view.password_confirmation.value:
            self.view.sign_up_button.disabled = False
        else:
            self.view.sign_up_button.disabled = True
        page.update()


    def _upon_switch_to_log_in_click(self, page: ft.Page):
        """
        Handles the user action of switching to the log-in view when the relevant
        button is clicked. Gathers the current username and password input by
        the user, then navigates to the log-in view with the provided credentials.

        :param page: An instance of `ft.Page` representing the application's current
            page state. Used for updating the UI after the navigation.
        """
        current_entry_username = ""
        current_entry_password = ""
        if self.view.username.value: current_entry_username = self.view.username.value
        if self.view.password.value: current_entry_password = self.view.password.value
        self.navigator(ViewsAndRoutesList.LOG_IN, username=current_entry_username, password=current_entry_password)
        page.update()

    def _upon_sign_up_click(self, page: ft.Page):
        """
        Handles the functionality triggered when the "Sign Up" button is clicked.

        The method validates user inputs (i.e., username and password), ensures they
        meet specific criteria, and performs user registration. It initiates hash
        generation for the password, encryption credentials creation for secure file
        handling, and communicates with the server to register the user.

        :param page: The page object for the Sign-Up interface.
        :type page: ft.Page
        :return: None
        """
        logging.info("Sign Up clicked")

        username, password = self.view.username.value, self.view.password.value

        if password != self.view.password_confirmation.value:
            logging.info("Passwords do not match.")
            page.open(error_alert("Password and Password Confirmation must be identical."))
            page.update()
            return

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


        salt, encrypted_file_master_key, nonce = self.file_encryption_service.create_new_encryption_credentials_from_password(password, new_file_master_key=True)

        logging.critical(f"Salt: {salt} \n Encrypted File Master Key: {encrypted_file_master_key} \n Nonce: {nonce}")

        status, response_data = self.comms_manager.send_message(Verbs.SIGN_UP, [username, password, salt, encrypted_file_master_key, nonce])
        if status == "SUCCESS":
            self.navigator(ViewsAndRoutesList.HOME)
        else:
            logging.info("Log In failed:")
            page.open(error_alert("Sign Up Failed: Username is already taken."))
            page.update()