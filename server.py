# https://stackoverflow.com/questions/24564587/communicate-between-a-processing-sketch-and-a-python-program

import socket
import logging


log = logging.getLogger()


class Server:

    def __init__(self, host='', port=5204):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.conn, self.addr = self.socket.accept()
        log.info("Socket to communicate with processing started")

    def barrier_triggered(self):
        try:
            self.conn.send("t")
        except BrokenPipeError:
            self.conn, self.addr = self.socket.accept()
            self.barrier_triggered()

    def new_receiver(self, address_id):
        try:
            self.conn.send(address_id)
        except BrokenPipeError:
            self.conn, self.addr = self.socket.accept()
            self.new_receiver(address_id)

    def start(self):
        try:
            self.conn.send("s")
        except BrokenPipeError:
            self.conn, self.addr = self.socket.accept()
            self.start()

    def payment_received(self):
        try:
            self.conn.send("p")
        except BrokenPipeError:
            self.conn, self.addr = self.socket.accept()
            self.payment_received()

    def payment_missing(self):
        try:
            self.conn.send("m")
        except BrokenPipeError:
            self.conn, self.addr = self.socket.accept()
            self.payment_missing()

    def end(self):
        try:
            self.conn.close()
        except BrokenPipeError:
            self.conn, self.addr = self.socket.accept()
            self.end()
