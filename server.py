import socket
import threading
import time
import select
import config as cf
from multiprocessing import Value


def threaded_client(conn: socket, other_conn: socket, last_send_time):
    conn.send(str.encode(str(conn)))
    reply = ""
    while True:
        try:
            data = conn.recv(2048)
            if not data:
                print("Disconnected")
                break
            reply = data.decode("utf-8")
            if reply == "Close Down":
                break

            current_time = time.time()
            if current_time - last_send_time.value >= 1.2:
                other_conn.sendall(data)
                last_send_time.value = current_time
            else:
                time.sleep(1.2)
                other_conn.sendall(data)
                last_send_time.value = current_time
        except Exception as e:
            print(f"error: {e}")
            break
    print("Lost connection")
    conn.close()


def start_home_server(result_queue):
    server = '0.0.0.0'
    # server =  socket.gethostbyname(socket.gethostname())
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
        # s.connect((server, port))

    except socket.error as e:
        print(e)

    s.listen(2)
    print("Server started, waiting for person")
    time.sleep(0.5)
    clients = []
    last_send_time = Value('d', time.time())  # Shared variable to store last send time
    while not cf.server_exit_flag:
        readable, _, _ = select.select([s], [], [], 1.0)
        if s in readable:
            try:
                conn, addr = s.accept()
                # print(f"Connected to {addr}")
                data = conn.recv(2048)
                reply = data.decode("utf-8")
                # print(f"reply is {reply}")

                if int(reply) != password:
                    print("Invalid password Issue")
                    conn.sendall(str.encode("Invalid Password Issue"))
                    conn.close()
                else:
                    print("Valid password")
                    clients.append(conn)
                    if len(clients) == 2:
                        client_thread1 = threading.Thread(target=threaded_client, args=(clients[0], clients[1], last_send_time))
                        client_thread2 = threading.Thread(target=threaded_client, args=(clients[1], clients[0], last_send_time))
                        client_thread1.start()
                        client_thread2.start()
            except Exception as e:
                print(f"Error: {e}")
    print("Server is exiting.")
    s.close()
