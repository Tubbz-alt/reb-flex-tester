import socket
import time
import struct


# Based on mclib by Thomas Schmid (http://github.com/tschmid/mclib)

class SCPI:
    def __init__(self, host, port):
        self.host = host
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

        self.f = self.s.makefile("rb")

        self.s.settimeout(1)

