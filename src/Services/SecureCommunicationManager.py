import logging
import socket
from os import urandom

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Dependencies.Constants import init_flag, end_flag, buffer_size, encryption_separator, resume_flag, host_addr
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SecureCommunicationManager:
    def __init__(self):
        self.sock: socket.socket = None
        self.encryption_key: bytes = None
        self.encryption_token: bytes = b""
        self.aesgcm = None
        self.needs_key_pair_creation = True
        self.is_connected = False

    def send_encrypted_message(self, message: bytes, retransmission: bool = False, will_send_data: bool = False) -> bytes:
        logging.debug(f"Sending encrypted message: {message}")
        logging.debug(f"Connecting to server...")

        if not self.is_connected:
            self._connect_to_server()
            self.is_connected = True

        if self.needs_key_pair_creation:
            logging.debug("Creating key pair and getting token...")
            self._create_key_pair_and_get_token()
            logging.debug("Key pair created successfully and token received.")
            self.needs_key_pair_creation = False

        logging.debug("Connected to server successfully.\nWriting encrypted message to send...")
        encrypted_message = self._write_encrypted_data(message) if not retransmission else message
        logging.debug(f"Encrypted message written successfully: {encrypted_message}")
        self.sock.sendall(encrypted_message)
        response =  self._receive_response(encrypted_message=encrypted_message)
        if not will_send_data:
            self.close_connection()
        return response

    def send_encrypted_data(self, data: bytes):
        encrypted_data = self._write_encrypted_data(data)
        logging.debug(f"Encrypted data written successfully: {encrypted_data}\nSending...")
        self.sock.sendall(encrypted_data)
        response = self._receive_response(encrypted_message=encrypted_data)
        self.close_connection()
        return response

    def close_connection(self):
        self.sock.close()
        self.is_connected = False

    def _receive_response(self, encrypted_message):
        data_parts = self._receive_data_parts_from_server()
        if data_parts[0] == init_flag:
            self.encryption_key = None
            self.encryption_token = b""
            self.needs_key_pair_creation = False
            return self.send_encrypted_message(encrypted_message, retransmission=True)
        else:
            self.encryption_token = data_parts[1]
            return self.aesgcm.decrypt(bytes(data_parts[2]), bytes(data_parts[3]), None)

    def _connect_to_server(self, host_address=host_addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(host_address)
        logging.info(f"Connected to: {host_addr}")

    def _create_key_pair_and_get_token(self):
        logging.debug("Initializing Secure Connection")

        private_key = x25519.X25519PrivateKey.generate()
        logging.debug("Generated Private Key")
        public_key = private_key.public_key()
        logging.debug("Generated Public Key")
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        logging.debug(f"Public Key Bytes: {public_key_bytes}")

        self.sock.sendall(self._write_encrypted_data(message=public_key_bytes, encryption_flag=init_flag, encrypt_message=False))
        logging.debug("Sent Initialization Flag and Public Key Bytes")

        data_parts = self._receive_data_parts_from_server()
        self.encryption_token, server_public_key_bytes = data_parts[1], data_parts[3]

        logging.debug(f"Received server public key bytes: {server_public_key_bytes}")
        server_public_key = serialization.load_pem_public_key(server_public_key_bytes)

        shared_key = private_key.exchange(server_public_key)
        logging.debug(f"Shared key: {shared_key.hex()}")

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"encryption key",
        ).derive(shared_key)

        self.encryption_key = derived_key
        logging.debug("Established Shared Key")

    def _write_encrypted_data(self, message: bytes = b"", encryption_flag: bytes = resume_flag, encrypt_message: bool = True) -> bytes:
        if not self.aesgcm and self.encryption_key:
            self.aesgcm = AESGCM(self.encryption_key)
        nonce = urandom(12)
        encrypted_message = self.aesgcm.encrypt(nonce, message, None) if message != b"" and encrypt_message else message
        return encryption_flag + encryption_separator + self.encryption_token + encryption_separator + nonce + encryption_separator + encrypted_message + end_flag

    def _receive_data_parts_from_server(self) -> list[bytes]:
        data = b""
        finished = False
        while not finished:
            data_chunk = self.sock.recv(buffer_size)
            data += data_chunk
            if data.endswith(end_flag):
                data = data[:-len(end_flag)]
                finished = True

        data_parts = data.split(encryption_separator)
        logging.debug(f"Received encrypted message: {data_parts}")
        return data_parts