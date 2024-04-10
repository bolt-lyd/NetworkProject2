from pydoc import cli
import socket
import threading
import datetime

################## Initializations ##################

# Define host IP and port
HOST = '127.0.0.1'
PORT = 12345

#Help Menu
help_menu = f"Commands:
- JOIN:
    Join the message board and assign your username.
    Example: JOIN;username
- POST:
    Post to the message board.
    Example: POST;Post Subject;Post body.
- USERS:
    Returns list of users in the message board.
    Example: USERS
- MESSAGE:
    Gets the Post body of the requested post.
    Example: MESSAGE;Id
- LEAVE:
    Leaves the given group.
    Example: LEAVE
- EXIT:
    Exit the server.
    Example: EXIT
- HELP:
    View the this menu again at any time.
    Example: HELP"

# Dictionary for tacking client information
client_info = {}
'''
client_info = {
    'user1': {
        'socket': client_socket1
    }
    'user2': {
        'socket': client_socket2
    }
}
'''
posts = {}
post_id = 0
################## /Initializations ##################


################## Functions ##################

# Handle incoming client connections
def handle_client(client_socket, client_address):
    
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data.startswith('CONNECT'):
                new_connection = data.split(';')
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((new_connection[1], new_connection[2]))
            elif data.startswith('JOIN'):
                username = data.split(';')[1]
                if username in client_info.keys():
                    client_socket.send("Username already exists. Please join with a new username.".encode("utf-8"))
                    client_socket.close()
                else:
                    client_info[username] = client_socket
                    client_socket.send(help_menu.encode)
                message = str(username) + " has joined the server"
                broadcast(message.encode())
            elif data.startswith('POST'):
                post_id += 1
                new_post = data.split(';')
                post = f"{post_id}, {username}, {datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")}, {new_post[1]}"
                posts[post_id] = {'username:', username, 
                                'date:', {datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")}, 
                                'subject:', {new_post[1]},
                                'body:', {new_post[2]}}
                broadcast(post)
            elif data.startswith('USERS'):
                message = "Users in group: " + {list(client_info.keys())}
                client_socket.send(message.encode("utf-8"))
            elif data.startswith('LEAVE'):
                user = client_info[username]
                message = str(username) + " has left the server"              
                broadcast(message.encode())
                del client_info[username]
            elif data.startswith('MESSAGE'):
                try:
                    message = data.split(';')
                    m = posts[message[1]]
                    post = f"User: , {m[0]['username']}, \nDate: , {m[0]['date']}, \nSubject: , {m[0]['subject']}, \nBody: {m[0]['body']}"
                    client_socket.send(post)
                except Exception as e:
                    client_socket.send("Message ID not found.")
            elif data.startswith('EXIT'):
                client_socket.close()
            elif data.startswith('HELP'):
                client_socket.send(help_menu.encode())
            else:
                client_socket.send('Not valid command'.encode("utf-8"))                

        except Exception as e:
            print("Error:", e)
            break

# Send message to everyone
def broadcast(message):
    for username in client_info.items():
        client_socket = client_info[username]
        try:
            client_socket.send(message.encode())
        except Exception as e:
            print("Error:", e)
        
################## /Functions ##################


################## Server connection ##################

# Create a socket for server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server listening on {HOST}:{PORT}")

################## /Sever connection ##################




try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Client connected from {client_address}")

        # New thread for handling the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_thread.start()))

except KeyboardInterrupt:
    print("Server shutting down...")
    # Close the server socket
    server_socket.close()