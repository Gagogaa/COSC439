import socket
import sys


# Parses the command line arguments for the
# corresponding option or returns the empty string
def arg_parse(option):
    for i in range(len(sys.argv)):
        if sys.argv[i] == option:
            return sys.argv[i + 1]
    return ""


# Get the host name from the command line or return the default value
def get_host():
    result = arg_parse("-h")
    return "localhost" if result == "" else result


# Get the port number from the command line or return the default value
def get_port():
    result = arg_parse("-p")
    return 56550 if result == "" else int(result)


# Get the username from the command line or return the default value
def get_username():
    # The default value should be the empty string
    return arg_parse("-u")


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
