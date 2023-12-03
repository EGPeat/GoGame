import socket


class Network:
    def __init__(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.32.64.164"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.pos = self.connect()
        print(self.get_pos())

    def get_pos(self):
        return self.pos

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            print("success")
            return ""
            #return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)
