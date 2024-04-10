import socket

# Define host IP and port
HOST = '127.0.0.1'
PORT = 12345

# Create a socket for server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Client connected from {client_address}")
