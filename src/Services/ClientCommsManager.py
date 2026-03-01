import json
import logging
from base64 import b64encode

from Dependencies.Constants import *
from Dependencies.VerbDictionary import Verbs
from Services.SecureCommunicationManager import SecureCommunicationManager


class ClientCommsManager:
    """
    Manages client-server communications, including request formatting, message
    sending, response handling, and token management.

    This class is responsible for facilitating secure and structured communication
    between a client application and its server. It provides methods for sending
    messages to the server, processing server responses, and handling specific
    protocol requirements such as secure connections, data transfer, and encoding.

    :ivar login_token: Authentication token used to authenticate client requests
        with the server. This token is dynamically updated based on the server
        responses.
    :type login_token: str
    :ivar secure_connection_manager: Instance of SecureCommunicationManager used to
        handle encrypted communication and data transfer with the server.
    :type secure_connection_manager: SecureCommunicationManager
    """
    def __init__(self):
        """
        Initializes an instance of the class with default attributes.
        """
        self.login_token = "no_token"
        self.secure_connection_manager = SecureCommunicationManager()

    def send_message(self, verb: Verbs, data: list):
        """
        Send a message to the secure connection manager with the specified verb and data. Handles processing of the
        response and, if necessary, performs additional communication steps based on the type of message being sent.

        :param verb: The action verb specifying the type of message being sent.
        :type verb: Verbs
        :param data: The list of data elements to be included in the message. For `CREATE_FILE` verb, the last element
                     of the list should contain the data to be sent after initial message exchange.
        :type data: list
        :return: A tuple containing the status and the response data received from the secure connection.
        :rtype: tuple
        """
        logging.info("Sending Message")
        logging.info(f"Verb: {verb.value}")
        message = self._write_message(verb, data if verb != Verbs.CREATE_FILE else data[:-1])

        logging.info(f"Sending Message: {message} \n waiting for response... \n")

        response = self.secure_connection_manager.send_encrypted_message(message.encode(), will_send_data=(verb == Verbs.CREATE_FILE))
        status, response_data = self._process_response(response)

        if response_data == "READY_FOR_DATA":
            logging.info("Sending data")
            str_to_send = data[-1]
            response = self.secure_connection_manager.send_encrypted_data(str_to_send)
            logging.info("Data sent \n waiting for response.")
            status,response_data = self._process_response(response)
        elif verb == Verbs.CREATE_FILE:
            self.secure_connection_manager.close_connection()

        return status, response_data

    def _process_response(self, response: bytes):
        """
        Processes the received response and extracts meaningful data based on specific flags and separators.

        :param response: The raw response received as a byte sequence.
        :type response: bytes

        :return: A tuple containing the extracted status and accompanying data, such as byte data,
            string data, or response code, depending on the format of the input response.
        :rtype: tuple
        """
        logging.info(f"Received Response: {response}")
        str_data = None
        byte_data = None
        if byte_data_flag in response:
            logging.info("Byte data flag found. Splitting response on byte data flag")
            response, byte_data = response.split(byte_data_flag)[0].decode(), response.split(byte_data_flag)[1]
        elif string_data_flag in response:
            logging.info("String data flag found. Splitting response on string data flag")
            response, str_data = response.split(string_data_flag)[0].decode(), response.split(string_data_flag)[1].decode()
        else:
            response = response.decode()

        response_parts = response.split(separator)
        status = response_parts[0]

        logging.info(f"Status: {status}")

        self.login_token = response_parts[1]
        logging.info(f"Saved Token: {self.login_token}")

        response_code = response_parts[2] if len(response_parts) > 2 else ""

        if byte_data:
            return status, (byte_data, response_code)
        elif str_data:
            return status, str_data
        else:
            return status, response_code

    def _write_message(self, verb: Verbs, data_parts: list):
        """
        Writes and encodes a message using a given verb and list of data parts. Ensures that each
        data part is appropriately encoded based on its type. Encoded messages are logged for
        debugging purposes and returned for further use.

        :param verb: An enumeration value representing the action or command to be included
                     in the message.
        :type verb: Verbs
        :param data_parts: A list containing the parts of the data to be included in the
                           message. Each part in the list is either a string or bytes. Strings
                           are kept as is, while bytes are Base64-encoded.
        :type data_parts: list
        :return: A string representing the encoded message, formatted to include the verb,
                 login token, and encoded data parts.
        :rtype: str
        """
        logging.info(f"Writing Message: {verb}, {data_parts}")
        decoded_parts = []
        for i in range(len(data_parts)):
            part = data_parts[i]
            if isinstance(part, str):
                decoded_parts.append((part, "str"))
            else:
                decoded_parts.append((b64encode(part).decode(), "bytes"))
        message = verb.value + separator + self.login_token + separator + json.dumps(decoded_parts)
        logging.info(f"Final Message: {message}")
        return message
