import socket
import sys


def get_host():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-h":
            return sys.argv[i + 1]

    return "localhost"


def get_port():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-p":
            return int(sys.argv[i + 1])

    return 56550


def get_username():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-u":
            return sys.argv[i + 1]

    return ""


def Main():
    host = get_host()
    port = get_port()
    username = get_username()
    run((host, port), username)


def run(address, username):
    # Create the Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(address)

    while username == "":
        username = input("Please enter a username: ")

    # Send the username
    s.send(username.encode())
    print("Enter messages:")

    while True:
        message = input("> ")
        s.send(message.encode())
        if message == "DONE":
            break

    # Receive the messages from the server
    result = s.recv(4096).decode()
    print(result)

    # Receive the connection time from the server
    result = s.recv(4096).decode()
    print(result)


Main()
