import datetime
import socket
import threading
from http import client
from pydoc import cli
from tokenize import group

################## Initializations ##################

# Define host IP and port
HOST = '127.0.0.1'
PORT = 12345

#Help Menu
help_menu = '''
Commands:
==JOIN==
Join the message board and assign your username.
Example: JOIN;username

==POST==
Post to the message board.
Example: POST;Post Subject;Post body.

==USERS==
Returns list of users in the message board.
Example: USERS

==MESSAGE==
Gets the Post body of the requested post.
Example: MESSAGE;Id

==LEAVE==
Leaves the given group.
Example: LEAVE

==GROUPS==
Retrieve a list of all groups that can be joined.
Example: GROUPS

==GROUPJOIN==
Join a specific group by name.
Example: GROUPJOIN;group_name

==GROUPPOST==
Post a message to a specific group's message board.
Example: GROUPPOST;group_name;post_subject;post_body.

==GROUPUSERS==
Retrieve a list of users in a specific group.
Example: GROUPUSERS;group_name

==GROUPMESSAGE==
Retrieve the content of a message posted earlier in a specific group's message board.
Example: GROUPMESSAGE;group_name;message_id

==GROUPLEAVE==
Leave a specific group.
Example: GROUPLEAVE;group_name

==EXIT==
Exit the server.
Example: EXIT

==HELP==
View this menu again at any time.
Example: HELP
'''

# Dictionary for tacking client information
client_info = {}
'''
client_info = {'user': 'client'}
'''
posts = {}
'''
posts = {
    id: {
        'username': 'user',
        'date': 'date time',
        'subject': 'post subject',
        'body': 'post body'
    },
    {
        ...
    }
}
'''

# Dictionary for tracking posts in each group
groups_posts = {'Group 1': {'posts': {}, 'users': []}, 'Group 2': {'posts': {}, 'users': []}, 'Group 3': {'posts': {}, 'users': []}, 'Group 4': {'posts': {}, 'users': []}, 'Group 5': {'posts': {}, 'users': []}}
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
            #decode data from client
            data = client_socket.recv(1024).decode()

            #get username being used by the client
            username = get_username(client_socket)

            #JOIN command
            #JOIN;{username}
            if data.startswith('JOIN'):
                username = data.split(';')[1]

                #if someone on the server already has the username, the server will not allow the user to join
                if username in client_info.keys():
                    client_socket.send("Username already exists. Please join with a new username.".encode("utf-8"))
                else:
                    #save client socket and username
                    client_info[username] = client_socket

                    #send last two posts on server to new user
                    if len(posts) > 1:
                        post = posts[post_id - 1]
                        client_socket.send(f"{post_id - 1}, {post['username']}, {post['date']}, {post['subject']}".encode())
                    if len(posts) > 0:
                        post = posts[post_id]
                        client_socket.send(f"{post_id}, {post['username']}, {post['date']}, {post['subject']}".encode())

                    #send message to everyone on the server that a new user has joined
                    message = f"{username} has joined the server"
                    broadcast(message)

            #POST;{subject};{body}
            elif data.startswith('POST'):

                #if user has not joined the server yet, they will be prompted to join the server first before any other commands can be made
                if not username:
                    client_socket.send("Please join the server first.".encode("utf-8"))
                else:
                    #get new post id
                    post_id += 1
                    new_post = data.split(';')
                    post = f"{post_id}, {username}, {datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}, {new_post[1]}"
                    posts[post_id] = {'username': username,
                                    'date': datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
                                    'subject': new_post[1],
                                    'body': new_post[2]}
                    #send new post to everyone on server
                    broadcast(post)

            # displays list of users currently in server group to the client
            elif data.startswith('USERS'):
                #if user has not joined server yet, they will be prompted to do so before making any more requests
                if not username:
                    client_socket.send("Please join the server first.".encode("utf-8"))
                else:
                    #get all of the usernames of the users currently on server
                    message = "Users in group: " + ", ".join(client_info.keys())
                    #send the message to user that requested the information
                    client_socket.send(message.encode("utf-8"))

            # Removes client from the server and alerts other users
            elif data.startswith('LEAVE'):
                #notify all users that a client has left the server
                message = str(username) + " has left the server"
                broadcast(message)
                #delete client's information
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
                #if user has not joined server, they will be prompted to do so before making any other requests
                if not username:
                    client_socket.send("Please join the server first.".encode("utf-8"))
                else:
                    #get list of joinable groups and send to user that requested the information
                    message = "Joinable Groups:\n" + "\n".join(groups_posts.keys())
                    client_socket.send(message.encode("utf-8"))

            # Add client to specific group
            elif data.startswith('GROUPJOIN'):
                group_data = data.split(';')
                group_name = group_data[1]
                # Check if valid group name
                if not username:
                    message = "Please join the group first."
                    client_socket.send(message.encode())
                else:

                    # Assign user to specified group
                    groups_posts[group_name]['users'].append(username)
                    group_posts = groups_posts[group_name]['posts']
                    post_keys = list(group_posts.keys())

                    if len(post_keys) > 1:
                            # Get the second-to-last post
                        second_last_post_id = post_keys[-2]
                        second_last_post = group_posts[second_last_post_id]
                        client_socket.send(f"{second_last_post_id}, {second_last_post['username']}, {second_last_post['date']}, {second_last_post['subject']}".encode())

                    if len(post_keys) > 0:
                            # Get the last post
                        last_post_id = post_keys[-1]
                        last_post = group_posts[last_post_id]
                        client_socket.send(f"{last_post_id}, {last_post['username']}, {last_post['date']}, {last_post['subject']}".encode())

                    message = f"\n{username} has joined {group_name}."
                    broadcast_group(message, group_name)


            #GROUPOST;group name;subject;body
            elif data.startswith('GROUPPOST'):
                group_data = data.split(';')
                if username not in groups_posts[group_data[1]]['users']:
                    message = "Please join group first."
                    client_socket.send(message.encode())
                else:
                    post_id += 1
                    post = f"{post_id}, {username}, {datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}, {group_data[2]}"
                    groups_posts[group_data[1]]['posts'][post_id] = {'username': username,
                                    'date': datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
                                    'subject': group_data[2],
                                    'body': group_data[3]}
                    #send new post to all users in group
                    broadcast_group(post, group_data[1])

            elif data.startswith('GROUPUSERS'):
                group_data = data.split(';')
                group_name = group_data[1]
                if username not in groups_posts[group_data[1]]['users']:
                    message = "Please join group first."
                    client_socket.send(message.encode())
                else:
                    if group_name in groups_posts:
                        users = ', '.join(groups_posts[group_name]['users'])
                        client_socket.send(f"Users in {group_name}: {users}".encode())
                    else:
                        client_socket.send(f"Group '{group_name}' not found.".encode())

            elif data.startswith('GROUPLEAVE'):
                leave_data = data.split(';')
                group_name = leave_data[1].strip()
                if group_name in groups_posts:
                    if username in groups_posts[group_data[1]]['users']:
                        groups_posts[group_name]['users'].remove(username)
                        message = f"{username} has left group {group_name}"
                        broadcast_group(message, group_name)
                    else:
                        client_socket.send("You are not a member of that group.".encode())
                else:
                    client_socket.send(f"{group_name} does not exist.".encode())

            elif data.startswith('GROUPMESSAGE'):
                message_data = data.split(';')
                group_name = message_data[1]
                message_id = message_data[2]
                if username not in groups_posts[group_name]['users']:
                    message = "Please join group first."
                    client_socket.send(message.encode())
                else:
                    if group_name in groups_posts:
                        post_info = groups_posts[group_name]['posts'][int(message_id)]
                        post_message = f"Post ID: {message_id}\nUsername: {post_info['username']}\nDate: {post_info['date']}\nSubject: {post_info['subject']}\nBody: {post_info['body']}"

                        client_socket.send(post_message.encode())
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

# Send message to everyone on server
def broadcast(message):
    #for all client sockets
    for client_socket in client_info.values():
        try:
            #send encoded message to all clients found in client_info
            client_socket.sendall(str(message).encode())
        except Exception as e:
            print("Error:", e)

# send message to everyone in a group given the message and group
def broadcast_group(message, group):
    #goes through each user in given group
    for user in groups_posts[group]['users']:
        try:
            #sends encoded message to client if username is found in group
            client_info[user].send(message.encode())
        except Exception as e:
            print("Error: ", e)

def get_username(client_socket):
    for key, value in client_info.items():
        if value == client_socket:
            return key
    return None  # If value is not found

# Create a socket for server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# HOST = input("Input server's host: ")
# PORT = int(input("Input server's port: "))
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server listening on {HOST}:{PORT}")

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
