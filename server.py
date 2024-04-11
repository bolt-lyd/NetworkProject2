import datetime
import socket
import threading
from pydoc import cli

################## Initializations ##################

# Define host IP and port
HOST = '127.0.0.1'
PORT = 12345

#Help Menu
help_menu = "Commands:\n- JOIN:\nJoin the message board and assign your username.\nExample: JOIN;username\n- POST:\nPost to the message board.\nExample: POST;Post Subject;Post body.\n- USERS:\nReturns list of users in the message board.\nExample: USERS\n- MESSAGE:\nGets the Post body of the requested post.\nExample: MESSAGE;Id\n- LEAVE:\nLeaves the given group.\nExample: LEAVE\n- EXIT:\nExit the server.\nExample: EXIT\n- HELP:\nView the this menu again at any time.\nExample: HELP"

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
username = None
################## /Initializations ##################


################## Functions ##################

# Handle incoming client connections
def handle_client(client_socket, client_address):
    global post_id
    global username
    while True:
        try:
            data = client_socket.recv(1024).decode()
            # if data.startswith('CONNECT'):
            #     new_connection = data.split(';')
            #     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #     client_socket.connect((new_connection[1], new_connection[2]))

            #tested;works
            if data.startswith('JOIN'):
                username = data.split(';')[1]
                if username in client_info.keys():
                    client_socket.send("Username already exists. Please join with a new username.".encode("utf-8"))
                else:
                    client_info[username] = client_socket
                    #client_socket.send(help_menu.encode())
                    if len(posts) > 1:
                        post = posts[post_id - 1]
                        client_socket.send(f"{post_id - 1}, {post['username']}, {post['date']}, {post['subject']}".encode())
                    if len(posts) > 0:
                        post = posts[post_id]
                        client_socket.send(f"{post_id}, {post['username']}, {post['date']}, {post['subject']}".encode())
                    message = f"{username} has joined the server"
                    broadcast(message)

            #tested; works
            elif data.startswith('POST'):
                if not username:
                    client_socket.send("Please join the server first.".encode("utf-8"))
                else:
                    post_id += 1
                    new_post = data.split(';')
                    post = f"{post_id}, {username}, {datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}, {new_post[1]}"
                    posts[post_id] = {'username': username,
                                    'date': datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
                                    'subject': new_post[1],
                                    'body': new_post[2]}
                    broadcast(post)

            # tested; works
            # displays list of users currently in server group to the client
            elif data.startswith('USERS'):
                if not username:
                    client_socket.send("Please join the server first.".encode("utf-8"))
                else:
                    message = "Users in group: " + ", ".join(client_info.keys())
                    client_socket.send(message.encode("utf-8"))

            elif data.startswith('LEAVE'):
                message = str(username) + " has left the server"
                broadcast(message)
                del client_info[username]
                break

            elif data.startswith('MESSAGE'):
                message = data.split(';')
                try:
                    post_info = posts[int(message[1])]
                    post_message = f"Post ID: {message[1]}\nUsername: {post_info['username']}\nDate: {post_info['date']}\nSubject: {post_info['subject']}\nBody: {post_info['body']}"
                    client_socket.send(post_message.encode())
                except:
                    client_socket.send("Post not found.".encode())

            #tested; works
            # terminates client
            elif data.startswith('EXIT'):
                client_socket.close()
                print(f"{client_address} disconnected")
                break

            #tested; works
            # prints help menu to the client
            elif data.startswith('HELP'):
                client_socket.send(help_menu.encode())

            else:
                client_socket.send('Not valid command'.encode("utf-8"))

        except Exception as e:
            print("Error:", e)
            break

# Send message to everyone
def broadcast(message):
    for client_socket in client_info.values():
        try:
            client_socket.sendall(str(message).encode())
        except Exception as e:
            print("Error:", e)

def get_post(id):
    return

################## /Functions ##################


################## Server connection ##################

# Create a socket for server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = input("Input server's host: ")
PORT = int(input("Input server's port: "))
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server listening on {HOST}:{PORT}")

################## /Sever connection ##################




try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Client connected from {client_address}")
        client_socket.send(help_menu.encode())

        # New thread for handling the client
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

except KeyboardInterrupt:
    print("Server shutting down...")
    # Close the server socket
    server_socket.close()
