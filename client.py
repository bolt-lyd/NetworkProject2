import socket
import sys
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QPushButton,
                             QTextEdit, QVBoxLayout, QWidget)

#default port; localhost
HOST = '127.0.0.1'

#default port
PORT = 12345

#client GUI class
class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.client_socket = None

    def initUI(self):

        #set up GUI window and define size
        self.setWindowTitle('Chat Client')
        self.setGeometry(100, 100, 600, 400)

        #text are of GUI that displays chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)

        #Input box for user to type message
        self.input_box = QLineEdit()

        #Send button; sends user inputted text to server
        self.send_button = QPushButton('Send')

        #layout
        layout = QVBoxLayout()
        layout.addWidget(self.chat_history)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.setLayout(layout)

        #GUI styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-size: 14px;
            }

            QTextEdit, QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
            }

            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 3px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.send_button.clicked.connect(self.send_message)
        self.input_box.returnPressed.connect(self.send_message)

    #adds message to chat history
    def append_message(self, message):
        self.chat_history.append(message)
        cursor = self.chat_history.textCursor()
        cursor.movePosition(cursor.End)
        self.chat_history.setTextCursor(cursor)

    #sends messages to server
    def send_message(self):
        if self.client_socket:
            message = self.input_box.text()
            self.client_socket.sendall(message.encode())
            self.input_box.clear()

    #recieves messages from server
    def receive_message(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if data:
                    self.append_message(data + '\n')
            except Exception as e:
                print(f"Error: {e}")
                break

    #start client and connect to server
    def start_client(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # HOST = input("Enter the address: ")
        # PORT = int(input("Enter the port: "))
        self.client_socket.connect((host, port))

        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.start()

#prompts use to input server's host and port
#defaults to localhost:12345
host = input("Input server's host: ")
port = input("Input server's port: ")

#if host entered by user, set HOST
if host:
    HOST = host

#if port entered by user, set PORT
if port:
    PORT = int(port)

#create PyQt appliation
app = QApplication(sys.argv)
#create new instance of client GUI
client_gui = ClientGUI()
#start client and connect to server
client_gui.start_client(HOST, PORT)
#display GUI
client_gui.show()
#run application on event loop
sys.exit(app.exec_())
