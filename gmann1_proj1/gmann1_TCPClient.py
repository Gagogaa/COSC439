import socket
import sys


# Get the host name from the command line or reutrn the default value
def get_host():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-h":
            return sys.argv[i + 1]

    return "localhost"


# Get the port number from the command line or reutrn the default value
def get_port():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-p":
            return int(sys.argv[i + 1])

    return 56550


# Get the username from the command line or reutrn the default value
def get_username():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-u":
            return sys.argv[i + 1]

    return ""


# Entry point for the program
def main():
    host = get_host()
    port = get_port()
    username = get_username()
    run((host, port), username)


def run(address, username):
    # Create an internet TCP socket
    # SOCK_STREAM is TCP. SOCK_DGRAM is UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to a server socket
    s.connect(address)

    # Prompt the user for a username until the user enters one
    while username == "":
        username = input("Please enter a username: ")

    # Send the username
    s.send(username.encode())
    print("Enter messages:")

    # Prompt the user for messages until they enter the terminal message
    while True:
        message = input("> ")
        # Send messages to the server
        s.send(message.encode())
        # DONE is the terminal message
        if message == "DONE":
            break

    # Receive the messages from the server
    result = s.recv(4096).decode()
    print(result)

    # Receive the connection time from the server
    result = s.recv(4096).decode()
    print(result)


main()
