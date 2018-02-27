#!/usr/bin/env python3
"""
Gregory Mann
COSC439 Computer Networking
The server component for the second project
"""


import socket
import sys
import os
import _thread
import threading
from datetime import datetime


CHATFILE = "gmann1_chat.txt"
DEFAULT_PORT = 56550
CONNECTED_USERS = 0
CLIENTS = {}
LOCK = threading.Lock()


def parse_args(option):
    """Parses the command line arguments for the
    corresponding option or return the empty string"""
    for i in range(len(sys.argv)):
        if sys.argv[i] == option:
            return sys.argv[i + 1]
    return ""


def timedelta_to_str(time):
    """Turn a timedelta object into a string"""
    hours = int(time.seconds / 3600)
    minutes = int((time.seconds / 60) - (hours * 60))
    seconds = int(time.seconds - (minutes * 60))
    milliseconds = int(time.microseconds / 1000)

    return str(hours) + "::" + str(minutes) + "::" + str(seconds) + "::" + str(milliseconds)


def get_host():
    """For the server this should always be localhost"""
    return "localhost"


def get_port():
    """Return the server port from the command line args or the default port"""
    result = parse_args("-p")
    return DEFAULT_PORT if result == "" else int(result)


def write_to_chat_file(message):
    """Write out the message to the chat file"""
    global CHATFILE
    global LOCK

    # Acquire a lock on this section of code
    LOCK.acquire()
    # Open the file for appending
    fout = open(CHATFILE, "a")
    # Append the message to the chat file
    fout.write(message)
    fout.flush()
    fout.close()
    # Release the lock
    LOCK.release()


def broadcast(message, sender):
    """Broadcast the message to all the other connected users and write
    the message to the chat file"""
    global CLIENTS
    message = message + "\n"

    # Print the message out on the server screen
    print(message, end='')

    # Write out the message to the chat file
    write_to_chat_file(message)

    # Send the message to all the *OTHER* clients
    for client in CLIENTS.values():
        if sender != client:
            client.send(message.encode())


def send_chatfile_messages(client):
    """Sends clients the messages from the charfile line by line"""
    global CHATFILE
    # Open the file for reading
    fin = open(CHATFILE, "r")

    # For every line in the file send it to the client
    s = fin.readline()

    # The empty string signifies the end of the file
    while s != "":
        client.send(s.encode())
        s = fin.readline()

    # Close the file
    fin.close()


def run(client):
    """Code to run when a client connects"""
    global CLIENTS
    global CONNECTED_USERS
    global CHATFILE

    # Start the connection time from right now
    start_time = datetime.now()

    # If this is the first user then create the chat file
    if CONNECTED_USERS == 0:
        # Open the file than immediately close it
        open(CHATFILE, "w").close()

    CONNECTED_USERS += 1

    # The first message from the client is the username
    user_name = client.recv(1024).decode()

    # Add "self" to the Threads dictionary
    CLIENTS[user_name] = client

    # Send the chat file to the connected client
    send_chatfile_messages(client)

    # Show an entrance message
    broadcast(user_name + ": has connected!", client)

    while True:
        # Get data from the user 1024 bytes at a time
        data = client.recv(1024).decode()
        # DONE is the terminal string so end the connection
        if data == "DONE":
            break

        # Send the data to all the other clients
        broadcast(user_name + ": " + data, client)

    # Send the connection time to the user
    connection_time = datetime.now() - start_time
    client.send(timedelta_to_str(connection_time).encode())

    # Close down the connection
    client.close()
    broadcast(user_name + ": has disconnected.", client)

    CONNECTED_USERS -= 1

    # Delete the chat file if no more users are connected
    if CONNECTED_USERS == 0:
        os.remove(CHATFILE)

    # Delete the thread from the client list
    del CLIENTS[user_name]


def main():
    """Entry point for the program"""
    host = get_host()
    port = get_port()

    # Create an internet TCP socket
    # SOCK_STREAM is TCP. SOCK_DGRAM is UDP
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to the socket
    soc.bind((host, port))
    # Listen for up to 10 connections
    soc.listen(10)

    # Wrap in a try..except to handle C-c keyboard Interrupts
    # So I can shutdown the server and free the socket
    # instead of "Crashing" the server.
    try:
        while True:
            # Accept is blocking so the server will wait for a
            # connection before continuing
            client, _ = soc.accept()
            # Create and start the new client thread
            _thread.start_new_thread(run, (client,))

    except KeyboardInterrupt:
        print("\nServer shutting down.")
    except:
        print("\nUnknown Server Error")
    finally:
        # Close the server socket
        soc.close()
        # Exit the program
        exit()


main()
