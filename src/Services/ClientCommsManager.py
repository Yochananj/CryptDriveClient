import json
import logging
from base64 import b64encode

from Dependencies.Constants import *
from Dependencies.VerbDictionary import Verbs
from Services.SecureCommunicationManager import SecureCommunicationManager


class ClientCommsManager:
    def __init__(self):
        self.login_token = "no_token"
        self.secure_connection_manager = SecureCommunicationManager()

    def send_message(self, verb: Verbs, data: list):
        logging.info("Sending Message")
        logging.debug(f"Verb: {verb.value}")
        message = self._write_message(verb, data if verb != Verbs.CREATE_FILE else data[:-1])

        logging.debug(f"Sending Message: {message} \n waiting for response... \n")

        response = self.secure_connection_manager.send_encrypted_message(message.encode(), will_send_data=(verb == Verbs.CREATE_FILE))
        status, response_data = self._process_response(response)

        if response_data == "READY_FOR_DATA":
            logging.debug("Sending data")
            str_to_send = data[-1]
            response = self.secure_connection_manager.send_encrypted_data(str_to_send)
            logging.debug("Data sent \n waiting for response.")
            status,response_data = self._process_response(response)
        elif verb == Verbs.CREATE_FILE:
            self.secure_connection_manager.close_connection()

        return status, response_data

    def _process_response(self, response: bytes):
        logging.debug(f"Received Response: {response}")
        str_data = None
        byte_data = None
        if byte_data_flag in response:
            logging.debug("Byte data flag found. Splitting response on byte data flag")
            response, byte_data = response.split(byte_data_flag)[0].decode(), response.split(byte_data_flag)[1]
        elif string_data_flag in response:
            logging.debug("String data flag found. Splitting response on string data flag")
            response, str_data = response.split(string_data_flag)[0].decode(), response.split(string_data_flag)[1].decode()
        else:
            response = response.decode()

        response_parts = response.split(separator)
        status = response_parts[0]

        logging.debug(f"Status: {status}")

        self.login_token = response_parts[1]
        logging.debug(f"Saved Token: {self.login_token}")

        response_code = response_parts[2]

        if byte_data:
            return status, (byte_data, response_code)
        elif str_data:
            return status, str_data
        else:
            return status, response_code

    def _write_message(self, verb: Verbs, data_parts: list):
        logging.debug(f"Writing Message: {verb}, {data_parts}")
        decoded_parts = []
        for i in range(len(data_parts)):
            part = data_parts[i]
            if isinstance(part, str):
                decoded_parts.append((part, "str"))
            else:
                decoded_parts.append((b64encode(part).decode(), "bytes"))
        message = verb.value + separator + self.login_token + separator + json.dumps(decoded_parts)
        logging.debug(f"Final Message: {message}")
        return message


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    client = ClientCommsManager()

    client.send_message(Verbs.LOG_IN, ["qwe", "qwe qwe qwe"])

    with open("/Users/yocha/Python Stuff/www/R8.jpg", "rb") as file:
        file_contents = file.read(-1)

    client.send_message(Verbs.CREATE_FILE, ["/", "R8.jpg", file_contents])