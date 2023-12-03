import socket
from time import sleep


class Network:
    def __init__(self, password=13, ip_address=None) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.32.64.164"
        if ip_address:
            self.server = ip_address
        self.port = 5555
        self.addr = (self.server, self.port)
        self.password = str(password)
        self.pos = self.connect()
        print(f"self.pos is {self.pos}")

    def get_pos(self):
        return self.pos

    def connect(self):
        retries = 3
        for _ in range(retries):
            try:
                self.client.connect(self.addr)
                print(f"Trying, here is password {self.password}\n")
                self.client.send(str(self.password).encode())
                return self.client.recv(2048).decode()
            except Exception as e:
                print(f"Error: {e}")
                print("Retrying...")
                sleep(1)
        return False

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            print("success")
            # return ""
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(f"error is {e}")
