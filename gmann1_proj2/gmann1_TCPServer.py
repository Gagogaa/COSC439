#!/usr/bin/env python3
"""
Gregory Mann
COSC439 Computer Networking
The server component for the second project

NOTE: Python code will only execute on 1 cpu core
even when using threads due to the global interpreter lock (GIL)
"""


# TODO: Put the connection time back in :(


import socket
import sys
import os
import _thread
import threading


CHATFILE = "gmann1_chat.txt"
DEFAULT_PORT = 56550
CONNECTED_USERS = 0
THREADS = {}
LOCK = threading.Lock()


def parse_args(option):
    """Parses the command line arguments for the
    corresponding option or return the empty string"""
    for i in range(len(sys.argv)):
        if sys.argv[i] == option:
            return sys.argv[i + 1]
    return ""


def get_host():
    """For the server this should always be localhost"""
    return "localhost"


def get_port():
    """Return the server port from the command line args or the default port"""
    result = parse_args("-p")
    return DEFAULT_PORT if result == "" else int(result)


class Client(threading.Thread):
    """Threading object used as a template for each of the clients"""
    user_name = ""
    client = None
    address = None


    def __init__(self, c, a):
        """__init__ is pythons version of a constructor"""
        global CONNECTED_USERS

        # Call the super class constructor
        threading.Thread.__init__(self)

        # If this is the first user then create the chat file
        if CONNECTED_USERS == 0:
            open(CHATFILE, "w").close()

        CONNECTED_USERS += 1
        self.client = c
        self.address = a


    def write_to_chat_file(self, message):
        """Write out the message to the chat file"""
        global CHATFILE
        global LOCK

        # Acquire a lock on this section of code
        LOCK.acquire()
        # Open the file for appending
        fout = open(CHATFILE, "a")
        # Append the message to the chat file
        fout.write(message + "\n")
        fout.flush()
        fout.close()
        # Release the lock
        LOCK.release()


    def read_chat_file(self):
        """Read all of the previous chat messages from the file"""
        global CHATFILE
        # Open the file for reading
        fin = open(CHATFILE, "r")
        # Read in the entire file
        messages = fin.read()
        fin.close()
        return messages


    def broadcast(self, message):
        """Broadcast the message to all the other connected users and write
        the message to the chat file"""
        # Prepend the user name to the message
        message = self.user_name + ": " + message

        # Print the message out on the server screen
        print(message)

        # Write out the message to the chat file
        self.write_to_chat_file(message)

        # Send the message to all the *OTHER* clients
        for name, value in THREADS.items():
            if self != value:
                value.client.send(message.encode())


    def run(self):
        """Code to run when a client connects"""
        global THREADS
        global CONNECTED_USERS
        global CHATFILE

        # The first message from the client is the username
        self.user_name = self.client.recv(1024).decode()

        # Add self to the Threads dictionary
        THREADS[self.user_name] = self

        # Send the chat file to the connected client
        self.client.send(self.read_chat_file().encode())

        # Show an entrance message
        self.broadcast("has connected!")

        while True:
            # Get data from the user 1024 bytes at a time
            data = self.client.recv(1024).decode()
            # DONE is the terminal string so end the connection
            if data == "DONE":
                break

            # Send the data to all the other clients
            self.broadcast(data)

        # Close down the connection and end the thread
        self.client.close()
        self.broadcast("has disconnected.")

        CONNECTED_USERS -= 1

        # Delet the chat file if no more users are connected
        if CONNECTED_USERS == 0:
            os.remove(CHATFILE)

        # Delete the thread from the list
        del THREADS[self.user_name]


# Keep the number of connections... delete the file when the number of connections is zero
def main():
    """Entry point for the program"""
    host = get_host()
    port = get_port()

    # Create an internet TCP socket
    # SOCK_STREAM is TCP. SOCK_DGRAM is UDP
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to the socket
    soc.bind((host, port))
    # Listen for only 1 connection (Don't buffer other connections)
    soc.listen(1)

    # Wrap in a try..except to handle C-c keyboard Interrupts
    # So I can shutdown the server and free the socket
    # instead of "Crashing" the server.
    try:
        while True:
            # Accept is blocking so the server will wait for a
            # connection before continuing
            client, address = soc.accept()
            # Create and start the new client thread
            Client(client, address).start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    except:
        print("\nUnknown Server Error")
    finally:
        soc.close()
        exit()


main()
