import logging
import socket
from os import urandom

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Dependencies.Constants import init_flag, end_flag, buffer_size, encryption_separator, resume_flag, host_addr
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SecureCommunicationManager:
    """
    Manages secure communication between a client and server using encryption.

    This class facilitates secure data exchange over a network by establishing encrypted communication.
    It supports sending encrypted messages and encrypted data, handles key pair creation for secure
    communication, and manages the lifecycle of the connection between the client and server.

    :ivar sock: The socket object used for network communication.
    :type sock: socket.socket
    :ivar encryption_key: The encryption key used for data encryption and decryption.
    :type encryption_key: bytes
    :ivar encryption_token: The token used for encryption and decryption processes.
    :type encryption_token: bytes
    :ivar aesgcm: The AES-GCM cipher object used for encryption and decryption.
    :type aesgcm: AESGCM
    :ivar needs_key_pair_creation: Specifies whether a new key pair needs to be created.
    :type needs_key_pair_creation: bool
    :ivar is_connected: Indicates whether the client is currently connected to the server.
    :type is_connected: bool
    """
    def __init__(self):
        """
        Manages a network connection with optional encryption capabilities.

        This class is responsible for initializing and maintaining a connection using
        a socket. It supports encryption using the AES-GCM algorithm and provides
        functionality to manage keys and tokens required for secure communication.
        """
        self.sock: socket.socket = None
        self.encryption_key: bytes = None
        self.encryption_token: bytes = b""
        self.aesgcm = None
        self.needs_key_pair_creation = True
        self.is_connected = False

    def send_encrypted_message(self, message: bytes, retransmission: bool = False, will_send_data: bool = False) -> bytes:
        """
        Sends an encrypted message to the server and retrieves the response.

        This method handles the process of connecting to the server, creating
        a key pair (if required), encrypting the message (if not retransmitting),
        sending the message, and receiving the server's response. If `will_send_data`
        is set to False, the connection is closed after the response is received.

        :param message: The message to send, in bytes.
        :type message: bytes
        :param retransmission: Specifies whether the message is a retransmission. If True,
            the message is sent without additional encryption. Defaults to False.
        :type retransmission: bool
        :param will_send_data: Indicates if further data will be sent after this message.
            If False, the connection is closed after sending the current message. Defaults to False.
        :type will_send_data: bool
        :return: The server's response to the sent message, in bytes.
        :rtype: bytes
        """
        logging.info(f"Sending encrypted message: {message}")
        logging.info(f"Connecting to server...")

        if not self.is_connected:
            self._connect_to_server()
            self.is_connected = True

        if self.needs_key_pair_creation:
            logging.info("Creating key pair and getting token...")
            self._create_key_pair_and_get_token()
            logging.info("Key pair created successfully and token received.")
            self.needs_key_pair_creation = False

        logging.info("Connected to server successfully.\nWriting encrypted message to send...")
        encrypted_message = self._write_encrypted_data(message) if not retransmission else message
        logging.info(f"Encrypted message written successfully: {encrypted_message}")
        self.sock.sendall(encrypted_message)
        response =  self._receive_response(encrypted_message=encrypted_message)
        if not will_send_data:
            self.close_connection()
        return response

    def send_encrypted_data(self, data: bytes):
        """
        Encrypts and sends data over a network connection. This method also logs the
        successful encryption and sending process, then handles the response. The
        connection is closed after the response is received.

        :param data: The raw binary data to be encrypted and sent.
        :type data: bytes
        :return: The response received from the recipient after sending the encrypted data.
        :rtype: Any
        """
        encrypted_data = self._write_encrypted_data(data)
        logging.info(f"Encrypted data written successfully: {encrypted_data}\nSending...")
        self.sock.sendall(encrypted_data)
        response = self._receive_response(encrypted_message=encrypted_data)
        self.close_connection()
        return response

    def close_connection(self):
        """
        Closes the connection by shutting down the socket and updating the connection
        status. This ensures that the communication channel is terminated and no
        further data can be sent or received through the socket.

        :return: None
        """
        self.sock.close()
        self.is_connected = False

    def _receive_response(self, encrypted_message):
        """
        Processes the response received from the server and decrypts the data.

        The function handles server response data by determining its type and
        processing it accordingly. If the server response indicates an initialization
        or re-authentication scenario, any existing encryption key or token is reset.
        Subsequently, it retransmits the encrypted message. Otherwise, it decrypts
        the received response using the AES-GCM encryption scheme.

        :param encrypted_message: The encrypted message to be sent for retransmission
                                  when re-initializing the encryption process.
                                  Must be provided in the form of bytes.
        :return: If responding to an initialization request, this function returns the
                 result of sending a retransmitted encrypted message. Otherwise, it
                 returns the decrypted data processed from the server response.
        :rtype: bytes
        """
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
        """
        Establishes a connection to a server using the provided host address.
        The method creates a socket, sets it to use TCP/IP protocol, and connects
        to the specified server address. Once the connection is established,
        it logs the connection status.

        :param host_address: The address of the server to connect to. Must be
            a tuple containing the hostname/IP and port.
        :type host_address: tuple[str, int]
        :return: None
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(host_address)
        logging.info(f"Connected to: {host_addr}")

    def _create_key_pair_and_get_token(self):
        """
        Generates a key pair, initiates secure communication with the server, and establishes
        a shared encryption key.

        The method involves creating a private-public key pair, sending the public key to the
        server, and receiving and processing the server's public key to derive a shared encryption
        key. Once complete, the derived key is set as the encryption key for secure communication.


        :return: None
        """
        logging.info("Initializing Secure Connection")

        private_key = x25519.X25519PrivateKey.generate()
        logging.info("Generated Private Key")
        public_key = private_key.public_key()
        logging.info("Generated Public Key")
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        logging.info(f"Public Key Bytes: {public_key_bytes}")

        self.sock.sendall(self._write_encrypted_data(message=public_key_bytes, encryption_flag=init_flag, encrypt_message=False))
        logging.info("Sent Initialization Flag and Public Key Bytes")

        data_parts = self._receive_data_parts_from_server()
        self.encryption_token, server_public_key_bytes = data_parts[1], data_parts[3]

        logging.info(f"Received server public key bytes: {server_public_key_bytes}")
        server_public_key = serialization.load_pem_public_key(server_public_key_bytes)

        shared_key = private_key.exchange(server_public_key)
        logging.info(f"Shared key: {shared_key.hex()}")

        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"encryption key",
        ).derive(shared_key)

        self.encryption_key = derived_key
        logging.info("Established Shared Key")

    def _write_encrypted_data(self, message: bytes = b"", encryption_flag: bytes = resume_flag, encrypt_message: bool = True) -> bytes:
        """
        Writes encrypted data to include encryption flag, separators, and end flag.

        If encryption is enabled and a valid message is provided, this method encrypts
        the message using AES-GCM with the provided key and random nonce. Otherwise,
        it appends the message directly. The output includes an encryption flag,
        encryption token, nonce, and the encrypted or plain message, combined with
        specific separators and an end flag.

        :param message: The message to be encrypted or appended directly.
        :type message: bytes

        :param encryption_flag: A byte sequence indicating the encryption status.
        :type encryption_flag: bytes

        :param encrypt_message: A flag indicating whether the message should be encrypted.
        :type encrypt_message: bool

        :return: A byte sequence containing the encrypted data, properly formatted
                 with encryption flag, separators, nonce, message, and end flag.
        :rtype: bytes
        """
        if not self.aesgcm and self.encryption_key:
            self.aesgcm = AESGCM(self.encryption_key)
        nonce = urandom(12)
        encrypted_message = self.aesgcm.encrypt(nonce, message, None) if message != b"" and encrypt_message else message
        return encryption_flag + encryption_separator + self.encryption_token + encryption_separator + nonce + encryption_separator + encrypted_message + end_flag

    def _receive_data_parts_from_server(self) -> list[bytes]:
        """
        Receives and processes data parts from the server socket until a specific end flag is encountered.
        The data is then split by an encryption separator into individual parts.

        :return: A list of data parts received from the server, split by the encryption separator.
        :rtype: list[bytes]
        """
        data = b""
        finished = False
        while not finished:
            data_chunk = self.sock.recv(buffer_size)
            data += data_chunk
            if data.endswith(end_flag):
                data = data[:-len(end_flag)]
                finished = True

        data_parts = data.split(encryption_separator)
        logging.info(f"Received encrypted message: {data_parts}")
        return data_parts