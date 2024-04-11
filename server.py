import datetime
from http import client
import socket
import threading
from pydoc import cli
from tokenize import group

################## Initializations ##################

# Define host IP and port
HOST = '127.0.0.1'
PORT = 12345

#Help Menu
help_menu = '''
Commands:
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

- GROUPS:
Retrieve a list of all groups that can be joined.
Example: GROUPS

- GROUPJOIN:
Join a specific group by name.
Example: GROUPJOIN;group_name

- GROUPPOST:
Post a message to a specific group's message board.
Example: GROUPPOST;group_name;post_subject;post_body.

- GROUPUSERS:
Retrieve a list of users in a specific group.
Example: GROUPUSERS;group_name

- GROUPMESSAGE:
Retrieve the content of a message posted earlier in a specific group's message board.
Example: GROUPMESSAGE;group_name;message_id

- GROUPLEAVE:
Leave a specific group.
Example: GROUPLEAVE;group_name

- EXIT:
Exit the server.
Example: EXIT

- HELP:
View this menu again at any time.
Example: HELP
'''


# Dictionary for tacking client information
client_info = {}
'''
client_info = {
    'user1': {
        'socket': client_socket1
    },
    'user2': {
        'socket': client_socket2
    },
    ...
}
'''
posts = {}

# Dictionary for tracking posts in each group
groups_posts = {}
'''
groups_posts = {
    'groupName1': {
        'posts': {
            1: {'username': 'user1', 'date': '2024-04-10 12:00:00', 'subject': 'Post 1 Subject', 'body': 'Post 1 Body'},
            2: {'username': 'user2', 'date': '2024-04-10 13:00:00', 'subject': 'Post 2 Subject', 'body': 'Post 2 Body'},
        },
        'users': {'user1', 'user2'}
    },
    'groupName2': {
        'posts': {},
        'users': {}
    },
}
'''


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

            # Removes client from the server and alerts other users
            elif data.startswith('LEAVE'):
                message = str(username) + " has left the server"
                broadcast(message)
                del client_info[username]
                break

            # Retrieves content of message given the message ID
            elif data.startswith('MESSAGE'):
                message = data.split(';')
                try:
                    post_info = posts[int(message[1])]
                    post_message = f"Post ID: {message[1]}\nUsername: {post_info['username']}\nDate: {post_info['date']}\nSubject: {post_info['subject']}\nBody: {post_info['body']}"
                    client_socket.send(post_message.encode())
                except:
                    client_socket.send("Post not found.".encode())
            
            # Retrieves list of all available groups
            elif data.startswith('GROUPS'):
                message = "Joinable Groups: " + ", ".join(groups_posts.keys())
                client_socket.send(message.encode("utf-8"))

            # Add client to specific group
            elif data.startswith('GROUPJOIN'):
                group_data = data.split(';')
                # Check if valid group name
                if len(group_data) < 2:
                    client_socket.send("Please provide a group name to join.".encode())
                else:
                    group_name = group_data[1].strip()
                    if group_name in groups_posts:
                        # Assign user to specified group
                        client_info[client_socket]['group'] = group_name
                        groups_posts[group_name]['users'].add(client_info[client_socket]['username'])
                        message = f"You have joined group {group_name}."
                        client_socket.send(message.encode())
                    else:
                        client_socket.send(f"Group {group_name} does not exist.".encode())
            
            #GROUPOST;group name;subject;body
            elif data.startswith('GROUPPOST'):
                group_data = data.split(';')
                if group_data[1] in groups_posts:
                    post_id += 1
                    post = f"{post_id}, {username}, {datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}, {new_post[2]}"
                    groups_posts[group_data[1]][post_id] = {'username': username,
                                    'date': datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
                                    'subject': new_post[2],
                                    'body': new_post[3]}
                    #new function; broadcast to group?
                    broadcast(post)
                    

            elif data.startswith('GROUPUSERS'):
                group_data = data.split(';')
                group_name = group_data[1]
                if group_name in groups_posts:
                    users = groups_posts[group_name]['users']
                    client_socket.send(f"Users in {group_name}: {', '.join(users)}")
                else:
                    client_socket.send(f"Group '{group_name}' not found.")

            elif data.startswith('GROUPLEAVE'):
                leave_data = data.split(';')
                group_name = leave_data[1].strip()
                if group_name in groups_posts:
                    if group_name in client_info[username]['groups']:
                        client_info[username]['groups'].remove(group_name)
                        groups_posts[group_name]['users'].discard(username)
                        message = f"You have left group {group_name}"
                        client_socket.send(message.encode())
                    else:
                        client_socket.send("You are not a member of that group.".encode())
                else:
                    client_socket.send(f"{group_name} does not exist.".encode())
             
            elif data.startswith('GROUPMESSAGE'):
                message_data = data.split(';')
                group_name = message_data[1]
                message_id = message_data[2]
                if group_name in groups_posts:
                    message = groups_posts[group_name][message_id]
                    post_message = f"Post ID: {message_id}\nUsername: {post_info['username']}\nDate: {post_info['date']}\nSubject: {post_info['subject']}\nBody: {post_info['body']}"

                    client_socket.send(f" {message[]}: {', '.join(users)}")
                else:
                    client_socket.send(f"Group '{group_name}' not found.")
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
            
# send message to everyone in group
def broadcast_group(message, group):
    for users in groups_posts[group]['users']:
        try:
            client_socket
lladnes

        


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
