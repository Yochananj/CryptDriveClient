"""
Provides password-related services, including verification and hashing.

This module facilitates secure password management by leveraging Argon2
for hashing and hmac for constant-time comparison. It integrates with
an external file encryption service to retrieve necessary cryptographic
keys and parameters for password verification and handling.

Classes:
    PasswordsService: Handles password verification and hashing functionalities.
"""

import hmac

from argon2.low_level import hash_secret_raw, Type

from Services.FileEncryptionService import FileEncryptionService


class PasswordsService:
    """
    Handles password verification and hashing functionalities.

    This class is responsible for verifying user passwords against encrypted keys
    and hashing passwords securely. It relies on external file encryption service
    to manage cryptographic operations.

    :ivar fes: The file encryption service providing encryption-related functionality.
    :type fes: object
    """
    def __init__(self, file_encryption_service: FileEncryptionService):
        """
        Initializes the instance with a file encryption service dependency.

        :param file_encryption_service: Service instance providing file encryption
            functionality.
        :type file_encryption_service: object
        """
        self.fes: FileEncryptionService = file_encryption_service

    def verify_password(self, password: str) -> bool:
        """
        Verifies whether the given password matches the stored derived key.

        This function compares a hashed version of the provided password, combined
        with the stored salt and specific hashing parameters, to the stored derived
        key. It uses the Argon2 hashing algorithm with predefined time cost, memory
        cost, parallelism, and hash length settings to ensure security.

        :param password: The password to verify.
        :type password: str
        :return: ``True`` if the password matches the stored derived key,
            ``False`` otherwise.
        :rtype: bool
        """
        return hmac.compare_digest(
            hash_secret_raw(
            secret=password.encode(),
            salt=self.fes.salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID
            ),
            self.fes.derived_key
        )
