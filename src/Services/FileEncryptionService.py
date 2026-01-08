import logging
from os import urandom

from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class FileEncryptionService:
    def __init__(self):
        self.encrypted_master_key: bytes = None
        self.encrypted_master_key_nonce: bytes = None
        self.derived_key: bytes = None
        self.derived_key_aesgcm: AESGCM = None

    def encrypt_file(self, file_bytes: bytes) -> tuple[bytes, bytes]:
        decrypted_file_master_key = self._decrypt_file_master_key()
        temp_aesgcm = AESGCM(decrypted_file_master_key)
        nonce: bytes = urandom(12)
        encrypted_file_bytes = temp_aesgcm.encrypt(nonce, file_bytes, None)
        return encrypted_file_bytes, nonce

    def decrypt_file(self, encrypted_file_bytes: bytes, file_nonce: bytes) -> bytes:
        decrypted_file_master_key = self._decrypt_file_master_key()
        temp_aesgcm = AESGCM(decrypted_file_master_key)
        decrypted_file_bytes = temp_aesgcm.decrypt(file_nonce, encrypted_file_bytes, None)
        return decrypted_file_bytes

    def derive_and_store_derived_key_from_password(self, password: str, salt: bytes) -> None:
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
        self.encrypted_master_key = encrypted_master_key
        self.encrypted_master_key_nonce = nonce

    def generate_encrypted_file_master_key(self) -> tuple[bytes, bytes]:
        file_master_key = AESGCM.generate_key(bit_length=256)
        logging.critical(f"File Master Key: {file_master_key}")

        encrypted_file_master_key, nonce = self._encrypt_file_master_key(file_master_key)
        logging.critical(f"Encrypted File Master Key: {encrypted_file_master_key}, Nonce: {nonce}")

        self.store_encrypted_master_key_and_nonce(encrypted_file_master_key, nonce)
        return encrypted_file_master_key, nonce

    def _encrypt_file_master_key(self, file_master_key: bytes) -> tuple[bytes, bytes]:
        nonce = urandom(12)
        encrypted_file_master_key = self.derived_key_aesgcm.encrypt(nonce, file_master_key, None)
        return encrypted_file_master_key, nonce

    def _decrypt_file_master_key(self) -> bytes:
        logging.critical(f"Decrypting File Master Key: {self.encrypted_master_key}\n Nonce: {self.encrypted_master_key_nonce}\nDerived Key: {self.derived_key}")
        return self.derived_key_aesgcm.decrypt(self.encrypted_master_key_nonce, self.encrypted_master_key, None)

