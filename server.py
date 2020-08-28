# https://stackoverflow.com/questions/24564587/communicate-between-a-processing-sketch-and-a-python-program

import socket
import logging


log = logging.getLogger()


class Server:

    def __init__(self, host='', port=5204):
        # FIXME in the methods, infinite recursive behaviour is possible
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.addr = None

    def connect(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.conn, self.addr = self.socket.accept()
        log.info("Socket to communicate with processing started")


    def barrier_triggered(self):
        try:
            self.conn.send(b"t")
        except BrokenPipeError as e:
            log.error("Connection to Socket died with error %s" % e)
            self.conn, self.addr = self.socket.accept()
            self.barrier_triggered()

    def new_receiver(self, address_id):
        try:
            self.conn.send(str(address_id).encode())
        except BrokenPipeError as e:
            log.error("Connection to Socket died with error %s" % e)
            self.conn, self.addr = self.socket.accept()
            self.new_receiver(address_id)

    def start(self):
        try:
            self.conn.send(b"s")
        except BrokenPipeError as e:
            log.error("Connection to Socket died with error %s" % e)
            self.conn, self.addr = self.socket.accept()
            self.start()

    def payment_received(self):
        try:
            self.conn.send(b"p")
        except BrokenPipeError as e:
            log.error("Connection to Socket died with error %s" % e)
            self.conn, self.addr = self.socket.accept()
            self.payment_received()

    def payment_missing(self):
        try:
            self.conn.send(b"m")
        except BrokenPipeError as e:
            log.error("Connection to Socket died with error %s" % e)
            self.conn, self.addr = self.socket.accept()
            self.payment_missing()

    def end(self):
        try:
            self.conn.close()
        except BrokenPipeError as e:
            log.error("Connection to Socket died with error %s" % e)
            self.conn, self.addr = self.socket.accept()
            self.end()
