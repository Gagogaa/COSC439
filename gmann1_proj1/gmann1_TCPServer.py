"""
Gregory Mann
COSC 439 Computer Networking
The server component for the first project
"""

import socket
import sys
import os
from datetime import datetime


CHATFILE = "gmann1_chat.txt"


def arg_parse(option):
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
    result = arg_parse("-p")
    return 56550 if result == "" else int(result)


def timedelta_to_str(time):
    """Turn a timedelta object into a string"""
    hours = int(time.seconds / 3600)
    minutes = int((time.seconds / 60) - (hours * 60))
    seconds = int(time.seconds - (minutes * 60))
    milliseconds = int(time.microseconds / 1000)

    return str(hours)+"::"+str(minutes)+"::"+str(seconds)+"::"+str(milliseconds)


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
            run(client, address)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    except:
        print("\nUnknown Server Error")
    finally:
        soc.close()


def run(client, address):
    """Code to run when a client connects"""
    print("User Connected ", address)
    # Start the connection time from right now
    start_time = datetime.now()
    # The first message from the client is the username
    username = client.recv(1024).decode()
    # Open the chat file for writing
    fout = open(CHATFILE, "w")

    while True:
        # Get data from the user 1024 bytes at a time
        data = client.recv(1024).decode()
        # DONE is the terminal string so end the connection
        if data == "DONE":
            break
        # Write the Clients messages to the chat file
        fout.write(username + " " + data + "\n")
        # Echo the messages from the user
        # print(data)
        # Flush the file output buffer as soon as the message is received
        # fout.flush()

    # Close the chat file
    fout.close()

    # Open the chat file for reading
    fin = open(CHATFILE, "r")
    # Read in the entire file
    messages = fin.read()
    fin.close()
    # Remove the chat file
    os.remove(CHATFILE)
    # Send the Client all the messages
    client.send(messages.encode())
    connection_time = datetime.now() - start_time
    # Send the Client the connection time
    client.send(timedelta_to_str(connection_time).encode())
    # End the connection
    client.close()
    print("User Disconnected ", address)


main()
