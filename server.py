import socket
import _thread as thr
import sys


def threaded_client(conn):
    conn.send(str.encode("Connected2"))
    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")

            if not data:
                print("Disconnected")
                break
            else:
                print(f"Recieved: {reply}")
                print(f"Sending reply: {reply}")
            conn.sendall(str.encode(reply))
        except:
            break
    print("Lost connection")
    conn.close()


def start_home_server():
    server = "10.32.64.164"
    # server = "192.168.122.1"
    # will be localhost
    port = 5555

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((server, port))

    except socket.error as e:
        print(e)

    s.listen(2)
    print("Server started, waiting for person")





    while True:
        conn, addr = s.accept()
        print(f"Connected to {addr}")
        thr.start_new_thread(threaded_client, (conn,))
