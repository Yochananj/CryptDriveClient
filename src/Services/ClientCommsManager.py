import logging
import socket

from Dependencies.Constants import *
from Dependencies.VerbDictionary import Verbs
from Services.ClientFileService import ClientFileService
from Services.PasswordHashingService import PasswordHashingService


class ClientClass:
    def __init__(self, log_out=None):
        self.sock: socket.socket = None
        self.file_service = ClientFileService()
        self.token = "no_token"
        self.navigator = log_out
        pass

    def send_message(self, verb: Verbs, data: list):
        logging.info("Sending Message")
        self.connect_to_server(host_addr)

        logging.debug(f"Verb: {verb.value}")
        message = self.write_message(verb, data if verb != Verbs.CREATE_FILE else data[:-1])


        self.sock.send(message.encode())
        logging.debug(f"Sent Message: {message} \n waiting for response. \n")

        a,b =  self.receive_response()

        if b == "READY_FOR_DATA":
            logging.debug("Sending data")
            str_to_send = data[-1] + end_flag
            self.sock.sendall(str_to_send)
            logging.debug("Data sent \n waiting for response.")
            a,b = self.receive_response()

        return a,b

    def receive_response(self):
        logging.debug("Receiving Response")
        finished = False
        response = ""
        previous_data_chunk = b""
        while not finished:
            data_chunk = self.sock.recv(buffer_size)
            response += data_chunk.decode()
            logging.debug(f"Received Data Chunk: {response[-len(data_chunk.decode()):]}")
            if (previous_data_chunk + data_chunk).endswith(end_flag):
                finished = True
                response = response[:-len(end_flag)]
            else:
                previous_data_chunk = data_chunk


        logging.debug(f"Received Response: {response}")
        str_data = None
        byte_data = None
        if bytes(byte_data_flag).decode() in response:
            logging.debug("Byte data flag found. Splitting response on byte data flag")
            response, byte_data = response.split(bytes(byte_data_flag).decode())[0], response.split(bytes(byte_data_flag).decode())[1]
        if bytes(string_data_flag).decode() in response:
            logging.debug("String data flag found. Splitting response on string data flag")
            response, str_data = response.split(bytes(string_data_flag).decode())[0], response.split(bytes(string_data_flag).decode())[1]

        response_parts = response.split(seperator)
        status = response_parts[0]

        logging.debug(f"Status: {status}")

        self.token = response_parts[1]
        logging.debug(f"Saved Token: {self.token}")

        self.sock.close()

        if byte_data:
            return status, byte_data
        elif str_data:
            return status, str_data
        else:
            return status, response_parts[2] if len(response_parts) > 2 else None

    def connect_to_server(self, host_address=host_addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(host_address)
        logging.info(('Connected to', host_addr))

    def write_message(self, verb: Verbs, data_parts: list):
        logging.debug(f"Writing Message: {verb}, {data_parts}")
        message = verb.value + seperator + self.token + seperator
        logging.debug(f"Current Message: {message}")
        for i in range(len(data_parts) - 1):
            message += data_parts[i] + seperator
            logging.debug(f"Current Message: {message}, index: {i}")
        message += data_parts[-1]
        logging.debug(f"Final Message: {message}")
        return message


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    client = ClientClass()

    client.send_message(Verbs.LOG_IN, ["qwe", PasswordHashingService.hash("qwe qwe qwe")])

    with open("/Users/yocha/Python Stuff/www/R8.jpg", "rb") as file:
        file_contents = file.read(-1)

    client.send_message(Verbs.CREATE_FILE, ["/", "R8.jpg", file_contents])

    client.sock.close()
