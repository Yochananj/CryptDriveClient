import hashlib

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
        return hash_secret_raw(
            secret=password.encode(),
            salt=self.fes.salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID
        ) == self.fes.derived_key

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes the given plain-text password using the SHA-256 algorithm and returns the generated hash.

        This method provides a secure, one-way hash for password verification or storage purposes. It
        transforms the input password string into a fixed-length hash string by utilizing the SHA-256
        algorithm from the hashlib module.

        :param password: The plain-text password to be hashed.
        :return: The resulting SHA-256 hash of the given password.
        """
        return hashlib.sha256(password.encode()).hexdigest()