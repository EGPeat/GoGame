import socket
import threading
import time
import select
import config as cf


def threaded_client(conn, other_conn):

    conn.send(str.encode("Connected"))
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
            if reply == "Close Down":
                break
            other_conn.sendall(str.encode(data))
        except Exception as e:
            print(f"Error: {e}")
            break
    print("Lost connection")
    conn.close()
    print(f"quit thread count: {threading.active_count()}")
    for thread in threading.enumerate():
        print(thread.name)


def start_home_server(result_queue):
    server = "10.32.64.164"
    # server = "192.168.122.1"
    # will be localhost
    # from random import randint
    # password = randint(1, 2**32-1)
    password = 5
    print(f"The server IP is {server}, and the password is {password}")
    port = 5555
    result_queue.put(password)
    result_queue.put(server)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((server, port))

    except socket.error as e:
        print(e)

    s.listen(2)
    print("Server started, waiting for person")
    time.sleep(0.5)
    clients = []
    while not cf.server_exit_flag:
        readable, _, _ = select.select([s], [], [], 1.0)
        if s in readable:
            try:
                conn, addr = s.accept()
                print(f"Connected to {addr}")
                data = conn.recv(2048)
                reply = data.decode("utf-8")
                print(f"reply is {reply}")

                if int(reply) != password:
                    print("Invalid password Issue")
                    conn.sendall(str.encode("Invalid Password Issue"))
                    conn.close()
                else:
                    print("Valid password")
                    clients.append(conn)
                    
                    if len(clients) == 2:
                        client_thread1 = threading.Thread(target=threaded_client, args=(clients[0], clients[1]))
                        client_thread2 = threading.Thread(target=threaded_client, args=(clients[1], clients[0]))
                        client_thread1.start()
                        client_thread2.start()
            except Exception as e:
                print(f"Error: {e}")
    print("Server is exiting.")
    s.close()
