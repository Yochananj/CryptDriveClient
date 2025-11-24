import math
import socket
import logging
import time

from Views.ViewsAndRoutesList import ViewsAndRoutesList
from Services.ClientFileService import ClientFileService
from Services.PasswordHashingService import PasswordHashingService
from Dependencies.Constants import *
from Dependencies.VerbDictionary import Verbs


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

        receiving_byte_data = False

        logging.debug(f"Verb: {verb.value}")
        message = self.write_message(verb, data if verb != Verbs.CREATE_FILE else data[:-1])

        if verb == Verbs.DOWNLOAD_FILE:
            receiving_byte_data = True

        self.sock.send(message.encode())
        logging.debug(f"Sent Message: {message} \n waiting for response. \n")

        a,b =  self.receive_response(receiving_byte_data)

        if b == "READY_FOR_DATA":
            logging.debug("Sending data")
            str_to_send = data[-1] + end_flag
            self.sock.sendall(str_to_send)
            logging.debug("Data sent \n waiting for response.")
            a,b = self.receive_response()

        return a,b

    def receive_response(self, is_receiving_byte_data=False):
        time.sleep(0.5)
        status = self.sock.recv(buffer_size).decode()

        logging.debug(f"Received and decoded: {status}")

        status_parts = status.split(seperator)

        to_return_data = ""
        if len(status_parts) == 3: to_return_data = status_parts[2]

        self.token = status_parts[1]
        logging.debug(f"Saved Token: {self.token}")


        if status_parts[0] == "ERROR":
            logging.debug("Error Occurred")
            logging.debug(f"Error Code: {to_return_data}")
        else:
            logging.debug("Request Successful")

        if to_return_data == "SENDING_DATA":
            logging.debug("Receiving Data")
            to_return_data = self.receive_data(is_receiving_byte_data)

        if to_return_data == "INVALID_TOKEN" and self.navigator:
            self.navigator(ViewsAndRoutesList.LOG_IN)
        return status_parts[0], to_return_data

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

    def receive_file(self):
        file_size = self.sock.recv(buffer_size).decode()
        logging.info(f"File size is: {file_size} bytes")

        file_bytes = self.receive_data(file_size)

        return file_bytes

    def receive_data(self, is_byte_data=False, file_size=None):
        finished = False
        index = 0
        if is_byte_data:
            received_data = b""
        else:
            received_data = ""

        logging.debug("Initializing data receiving")

        while not finished:
            data_chunk = self.sock.recv(buffer_size)

            index += 1
            if index % 10 == 0 and file_size:
                logging.debug(f"received data chunk {index} / {math.ceil(int(file_size) / buffer_size)}")

            if data_chunk.endswith(end_flag):
                finished = True
                if is_byte_data: received_data += data_chunk[:-len(end_flag)]
                else: received_data += data_chunk[:-len(end_flag)].decode()
            else:
                if is_byte_data: received_data += data_chunk
                else: received_data += data_chunk.decode()

        logging.info(f"finished receiving data: {received_data}, {type(received_data)}")

        return received_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    client = ClientClass()

    client.send_message(Verbs.LOG_IN, ["qwe", PasswordHashingService.hash("qwe qwe qwe")])

    with open("/Users/yocha/Python Stuff/www/R8.jpg", "rb") as file:
        file_contents = file.read(-1)

    client.send_message(Verbs.CREATE_FILE, ["/", "R8.jpg", file_contents])

    client.sock.close()
