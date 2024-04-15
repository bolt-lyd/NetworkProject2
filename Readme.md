# Socket Programming Bulletin Board
### How to run
Before running this program for the first time, in the termninal run `make requirements` in the root directory to ensure that you have all of the required imports.

In the terminal, run `make run_server` in the root directory. User will be prompted to enter a host address and port. If you want to use the default host and port (127.0.0.1:12345), then click 'Enter' for both.

If done correctly, you should see `Server listening on HOST:PORT`.

If there is something already running on the netowrk address/port, `server.py` will exit with error `OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted`.

To run a client, open a new terminal and run `make run_client` in the root directory. User will be prompted to enter a host address and port. If you want to use the default host and port(127.0.0.1:12345), then click 'Enter' for both.

If done correctly, the client GUI will open in a new window.

If there is no server running at that address, `client.py` will exit with error `ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it`.

> [!NOTE]
> When the client GUI starts, you will see `QObject::connect: Cannot queue arguments of type 'QTextCursor'
(Make sure 'QTextCursor' is registered using qRegisterMetaType().)` in the terminal. This is not an error that effects the performance of the program, as far as has been observed.

### How to use
When the client's GUI opens, it will display a welcome message, as well as a help menu with all of the available commands. To see this help menu again at any time, send "HELP" and the menu will display to the user again.

### Authors
Madison Barry, Kelly Deal, and Lydia Watchman
