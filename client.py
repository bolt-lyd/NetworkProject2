import socket
import threading


# send messages
def send_message(client_socket):
    while True:
        message = input()
        client_socket.sendall(message.encode())


def receive_message(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                print(data + '\n')
        except Exception as e:
            print(f"Error: ", e)
            break

#start client
def start_client():
    server_address = input("Enter server address: ")
    server_port = int(input("Enter server port: "))
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    send = threading.Thread(target=send_message, args=(client_socket,))
    receive = threading.Thread(target=receive_message, args=(client_socket,))

    send.start()
    receive.start()

# Start the client
start_client()
