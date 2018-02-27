#!/usr/bin/env python3
"""
Gregory Mann
COSC439 Computer Networking
The client component for the second project
"""


import socket
import sys
import _thread


DEFAULT_PORT = 56550


def parse_args(option):
    """Parses the command line arguments for the
    corresponding option or returns the empty string"""
    for i in range(len(sys.argv)):
        if sys.argv[i] == option:
            return sys.argv[i + 1]
    return ""


def get_host():
    """Get the host name from the command line or return the default value"""
    result = parse_args("-h")
    return "localhost" if result == "" else result


def get_port():
    """Get the port number from the command line or return the default value"""
    result = parse_args("-p")
    return DEFAULT_PORT if result == "" else int(result)


def get_username():
    """Get the username from the command line or return the default value"""
    # The default value should be the empty string
    user_name = parse_args("-u")

    # Prompt the user for a username until the user enters one
    while user_name == "":
        user_name = input("Please enter a username: ")

    return user_name


def main():
    """Entry point for the program"""
    host = get_host()
    port = get_port()
    username = get_username()
    run((host, port), username)


def display_thread(soc):
    """Print messages that the application gets from the server"""
    while True:
        print(soc.recv(1024).decode(), end='')


def run(address, username):
    """Run client code"""
    # Create an internet TCP socket
    # SOCK_STREAM is TCP. SOCK_DGRAM is UDP
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to a server socket
    soc.connect(address)

    # Send the username
    soc.send(username.encode())

    # Start a thread that handles printing messages from the server
    _thread.start_new_thread(display_thread, (soc,))

    print("Enter messages:")

    # Prompt the user for messages until they enter the terminal message
    # Wrap in a try..except to handle C-c keyboard Interrupts
    # So I can send DONE without crashing the program (or the server)
    try:
        while True:
            message = input("")
            # Send messages to the server
            soc.send(message.encode())
            # DONE is the terminal message
            if message == "DONE":
                break
    except KeyboardInterrupt:
        # Send DONE if the user enters C-c
        soc.send("DONE".encode())
    finally:
        # Print out the connection time from the server
        print(soc.recv(1024).decode())
        # Exit the program
        exit()


main()
