import socket
from time import sleep


class Network:
    def __init__(self, password=13, ip_address=None) -> None:
        '''
        Initializes a Network object.
        Args:
            password: The password for connecting to the server.
            ip_address: The IP address of the server.
        '''
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "172.22.16.1"
        if ip_address:
            self.server = ip_address
        self.port = 5555
        self.addr = (self.server, self.port)
        self.password = str(password)
        self.pos = self.connect()
        self.message_in = ''

    def get_pos(self):
        '''Gets the position.'''
        return self.pos

    def connect(self):
        '''Connects to the server, with 3 tries.'''
        retries = 3
        for _ in range(retries):
            try:
                self.client.connect(self.addr)
                self.client.send(str(self.password).encode())
                return self.client.recv(2048).decode()
            except Exception as e:
                print(f"Error: {e}")
                print("Retrying...")
                sleep(1)
        return False

    def send(self, data):
        '''Sends data to the server.'''
        try:
            self.client.sendall(str.encode(data))
            return self.client.recv(2048).decode()
        except Exception as e:
            print(f"error is {e}")

    def send_and_recieve(self, data):
        '''Sends data to the server and waits until it recieves a reply.'''
        try:
            self.client.sendall(str.encode(data))
            reply = self.client.recv(2048).decode("utf-8")
            self.message_in = reply
            return True
        except Exception as e:
            print(f"error is {e}")
            return False

    def first_round_op(self):
        '''Performs the first-round operation.'''
        try:
            if self.message_in == '':
                reply = self.client.recv(2048).decode("utf-8")
                self.message_in = reply
                print("worked22")
                return True
            else:
                return True
        except Exception as e:
            print(f"error is {e}")
            return False

    def recv(self, size):
        '''Recieves data from the server.'''
        try:
            info = self.client.recv(size).decode("utf-8")
            return info
        except Exception as e:
            print(f"error is {e}")
