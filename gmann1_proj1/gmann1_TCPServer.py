import socket
import sys
import os
from datetime import datetime


chatfile = "gmann1_chat.txt"


# Parses the command line arguments for the
# corresponding option or return the empty string
def arg_parse(option):
    for i in range(len(sys.argv)):
        if sys.argv[i] == option:
            return sys.argv[i + 1]
    return ""


# For the server this should always be localhost
def get_host():
    return "localhost"


# Return the server port from the command line args or the default port
def get_port():
    result = arg_parse("-p")
    return 56550 if result == "" else int(result)


# Turn a timedelta object into a string
def timedelta_to_str(t):
    hours = int(t.seconds / 3600)
    minutes = int((t.seconds / 60) - (hours * 60))
    seconds = int(t.seconds - (minutes * 60))
    milliseconds = int(t.microseconds / 1000)

    return str(hours)+"::"+str(minutes)+"::"+str(seconds)+"::"+str(milliseconds)


# Entry point for the program
def main():
    host = get_host()
    port = get_port()

    # Create an internet TCP socket
    # SOCK_STREAM is TCP. SOCK_DGRAM is UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to the socket
    s.bind((host, port))
    # Listen for only 1 connection (Don't buffer other connections)
    s.listen(1)

    # Wrap in a try..except to handle C-c keyboard Interrupts
    # So I can shutdown the server and free the socket
    # instead of "Crashing" the server.
    try:
        while True:
            # Accept is blocking so the server will wait for a
            # connection before continuing
            client, address = s.accept()
            run(client, address)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    except:
        print("\nUnknown Server Error")
    finally:
        s.close()


def run(client, address):
    print("User Connected ", address)
    # Start the connection time from right now
    start_time = datetime.now()
    # The first message from the client is the username
    username = client.recv(1024).decode()
    # Open the chat file for writing
    fout = open(chatfile, "w")

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
    fin = open(chatfile, "r")
    # Read in the entire file
    messages = fin.read()
    fin.close()
    # Remove the chat file
    os.remove(chatfile)
    # Send the Client all the messages
    client.send(messages.encode())
    connection_time = datetime.now() - start_time
    # Send the Client the connection time
    client.send(timedelta_to_str(connection_time).encode())
    # End the connection
    client.close()
    print("User Disconnected ", address)


main()
