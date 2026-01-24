import hashlib

from argon2.low_level import hash_secret_raw, Type


class PasswordsService:
    def __init__(self, file_encryption_service):
        self.fes = file_encryption_service

    def verify_password(self, password: str) -> bool:
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
        return hashlib.sha256(password.encode()).hexdigest()