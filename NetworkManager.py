import socket
import time

class NetworkManager():
    def __init__(self, sock=None):
        self.host = "127.0.0.1"
        self.port = 5065
        print("UDP target IP:", self.host)
        print("UDP target port:", self.port)

        if sock is None:
            self.sock = socket.socket(socket.AF_INET, # Internet
                                socket.SOCK_DGRAM) # UDP
            
        else:
            self.sock = sock
        

    def connect(self):
        self.sock.connect((self.host, self.port))

    def send_coord(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.sendto(msg[totalsent:].encode(), (self.host, self.port))
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
                             
                    