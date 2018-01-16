import socket
import sys
import os
from datetime import datetime


def get_host():
    return "localhost"


def get_port():
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-p":
            return int(sys.argv[i + 1])

    return 56550


def timedelta_to_str(t):
    hours = int(t.seconds / 3600)
    minutes = int((t.seconds / 60) - (hours * 60))
    seconds = int(t.seconds - (minutes * 60))
    milliseconds = int((t.microseconds / 1000))

    return str(hours)+"::"+str(minutes)+"::"+str(seconds)+"::"+str(milliseconds)


def Main():
    host = get_host()
    port = get_port()

    # Open an internet TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)

    # Wrap in a try except to handle C-c keyboard Interrupts
    # So I can free the socket instead of "Crashing" the server.
    try:
        while True:
            # Accept is blocking so the server will wait for a connection before continuing
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
    filename = "gm_chat.txt"
    timenow = datetime.now()
    username = client.recv(1024).decode() # The first message is the username
    fout = open(filename, "w")

    while True:
        data = client.recv(1024).decode()
        if data == "DONE": # If their is no more data end the communication
            break
        # print(data) # Echo the messages
        fout.write(username + " " + data + "\n")
        print(data)
        # Adding this back in will flush the output buffer writing the file to disk
        fout.flush()

    fout.close()
    fin = open(filename, "r")
    messages = fin.read() # Reads in the entire file by default
    fin.close()
    os.remove(filename)
    client.send(messages.encode())
    client.send(timedelta_to_str(datetime.now() - timenow).encode())
    print("User Disconnected ", address)
    client.close()


Main()
