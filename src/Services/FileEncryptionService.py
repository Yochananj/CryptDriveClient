import logging
from os import urandom

from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class FileEncryptionService:
    """
    Represents a service for handling file encryption and decryption. This service
    manages cryptographic key generation, derivation, encryption, and decryption
    processes using AES-GCM for secure file encryption workflows.

    :ivar encrypted_master_key: Stores the encrypted master key for file encryption.
    :type encrypted_master_key: bytes
    :ivar encrypted_master_key_nonce: Stores the nonce used during encryption of the
        master key.
    :type encrypted_master_key_nonce: bytes
    :ivar derived_key: Stores the cryptographic key derived from a password and salt
        using the Argon2 key derivation function.
    :type derived_key: bytes
    :ivar derived_key_aesgcm: Stores an instance of AESGCM initialized with the
        derived key, providing authenticated encryption and decryption operations.
    :type derived_key_aesgcm: AESGCM
    :ivar salt: Stores the salt used in the key derivation function.
    :type salt: bytes
    """
    def __init__(self):
        """
        Represents a cryptographic key management system that handles encrypted master
        keys, derived keys, and associated cryptographic operations.
        """
        self.encrypted_master_key: bytes = None
        self.encrypted_master_key_nonce: bytes = None
        self.derived_key: bytes = None
        self.derived_key_aesgcm: AESGCM = None
        self.salt: bytes = None

    def create_new_encryption_credentials_from_password(self, password, new_file_master_key=False):
        """
        Creates new encryption credentials from a given password. Depending on whether a new
        file master key is specified, it generates and stores encryption data either for a
        new file master key or by re-encrypting an existing file master key.

        This method handles the derivation and storage of keys and also manages the storage
        of encrypted file master keys and associated nonces.

        :param password: The password from which encryption credentials are derived.
        :type password: str
        :param new_file_master_key: Flag to determine if a new file master key should be
            generated and used. Defaults to False.
        :type new_file_master_key: bool
        :return: A tuple containing the salt, encrypted file master key, and nonce.
        :rtype: tuple
        """
        salt = urandom(16)
        if new_file_master_key:
            self.derive_and_store_derived_key_from_password_and_salt(password, salt)
            encrypted_file_master_key, nonce = self._generate_encrypted_file_master_key()
            self.store_encrypted_master_key_and_nonce(encrypted_file_master_key, nonce)
        else:
            decrypted_file_master_key = self._decrypt_file_master_key()
            self.derive_and_store_derived_key_from_password_and_salt(password, salt)
            encrypted_file_master_key, nonce = self._encrypt_file_master_key(decrypted_file_master_key)
            self.store_encrypted_master_key_and_nonce(encrypted_file_master_key, nonce)
        return salt, encrypted_file_master_key, nonce

    def derive_and_store_derived_key_from_password_and_salt(self, password: str, salt: bytes) -> None:
        """
        Derives a cryptographic key from the provided password and salt, then stores the resulting
        key and AES-GCM object internally. This method uses a secure password hashing algorithm
        and is designed to ensure integrity and confidentiality of the derived key.

        :param password: The password to be derived into a cryptographic key.
        :type password: str
        :param salt: The cryptographic salt used in the derivation process.
        :type salt: bytes
        :return: This method does not return anything. The derived key and AES-GCM object are
                 stored internally.
        :rtype: None
        """
        self.salt = salt
        self.derived_key = hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID
        )
        self.derived_key_aesgcm = AESGCM(self.derived_key)

    def store_encrypted_master_key_and_nonce(self, encrypted_master_key: bytes, nonce: bytes) -> None:
        """
        Stores an encrypted master key and its associated nonce for future retrieval. This method allows
        saving sensitive cryptographic material securely.

        :param encrypted_master_key: The encrypted master key to be stored.
        :type encrypted_master_key: bytes
        :param nonce: The nonce associated with the encrypted master key.
        :type nonce: bytes
        :return: None
        """
        self.encrypted_master_key = encrypted_master_key
        self.encrypted_master_key_nonce = nonce

    def encrypt_file(self, file_bytes: bytes) -> tuple[bytes, bytes]:
        """
        Encrypts the given file using a decrypted file master key and AES-GCM encryption. This method
        utilizes a randomly generated nonce for encryption.

        :param file_bytes: The content of the file to be encrypted, represented as a bytes object.
        :return: A tuple containing the encrypted file content and the nonce used for encryption.
        """
        decrypted_file_master_key = self._decrypt_file_master_key()
        temp_aesgcm = AESGCM(decrypted_file_master_key)
        nonce: bytes = urandom(12)
        encrypted_file_bytes = temp_aesgcm.encrypt(nonce, file_bytes, None)
        return encrypted_file_bytes, nonce

    def decrypt_file(self, encrypted_file_bytes: bytes, file_nonce: bytes) -> bytes:
        """
        Decrypts an encrypted file using the provided nonce and the decrypted file master key.

        This method utilizes the AES-GCM (Advanced Encryption Standard Galois/Counter Mode)
        algorithm to decrypt a file that was encrypted with the corresponding file master
        key.

        :param encrypted_file_bytes: The encrypted file content in bytes.
        :param file_nonce: The nonce (number used once) used during the encryption process,
            provided as bytes.
        :return: The decrypted file content in bytes.
        :rtype: bytes
        """
        decrypted_file_master_key = self._decrypt_file_master_key()
        temp_aesgcm = AESGCM(decrypted_file_master_key)
        decrypted_file_bytes = temp_aesgcm.decrypt(file_nonce, encrypted_file_bytes, None)
        return decrypted_file_bytes

    def _generate_encrypted_file_master_key(self) -> tuple[bytes, bytes]:
        """
        Generates and encrypts a file master key using AES-GCM.

        This method creates a new 256-bit file master key and encrypts it using
        a secure encryption mechanism. It also generates a nonce for the encryption
        process. The encrypted file master key and the nonce are returned as a tuple.

        :return: A tuple containing the encrypted file master key and the nonce.
        :rtype: tuple[bytes, bytes]
        """
        file_master_key = AESGCM.generate_key(bit_length=256)

        encrypted_file_master_key, nonce = self._encrypt_file_master_key(file_master_key)

        return encrypted_file_master_key, nonce

    def _encrypt_file_master_key(self, file_master_key: bytes) -> tuple[bytes, bytes]:
        """
        Encrypts the given file master key using AES-GCM encryption mode with a
        randomly generated nonce.

        This method ensures the encryption of the file master key using a secure
        generated nonce to provide confidentiality and integrity. The encryption
        is performed using a derived AES-GCM key, which should already be initialized
        prior to calling this method.

        :param file_master_key: The file master key to be encrypted. It should be
                                provided as a byte sequence.
        :return: A tuple containing the encrypted file master key and the generated
                 nonce. The encrypted file master key is a byte sequence, and the nonce
                 is a randomly generated byte sequence.
        """
        nonce = urandom(12)
        encrypted_file_master_key = self.derived_key_aesgcm.encrypt(nonce, file_master_key, None)
        return encrypted_file_master_key, nonce

    def _decrypt_file_master_key(self) -> bytes:
        """
        Decrypts the encrypted file master key using AES-GCM encryption.

        This method utilizes a derived AES-GCM key and a nonce to perform the decryption
        of the encrypted file master key, enabling secure access to encrypted file contents.

        :return: The decrypted file master key.
        :rtype: bytes
        """
        logging.critical(f"Decrypting File Master Key: {self.encrypted_master_key}\n Nonce: {self.encrypted_master_key_nonce}\nDerived Key: {self.derived_key}")
        return self.derived_key_aesgcm.decrypt(self.encrypted_master_key_nonce, self.encrypted_master_key, None)
