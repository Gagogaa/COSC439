Greogry Mann
Project 2
Time: 6 hours


# Before running the program
First check the python version:
```
>$ python --version
Python 2.7.14
```

If the version is less than "3.3.0" try:
```
>$ python3 --version
python3: command not found...
```

If the command does not exist please install python 3 from:
https://www.python.org/downloads/release/python-364/



# Running the program
(Assuming python 3 is accessable via the python3 command)
The server must start first:
```
>$ python3 gmann1_TCPServer.py
```

Connecting with the client:
```
>$ python3 gmann1_TCPClient.py
```

The Server program can take in a port number argument with "-p":
```
>$ python3 gmann1_TCPServer -p 55566
```

The Client program can take in tree arguments, a port number "-p",
a host name "-h", and a user name "-u":
```
>$ python3 gmann1_TCPClient.py -u myName -p 55566 -h localhost
```

To stop the Server press "C-c" (Hold control and hit c) at the command line:
```
>$ python3 gmann1_TCPServer.py
User Connected  ('127.0.0.1', 37700)
User Disconnected  ('127.0.0.1', 37700)
^C
Server shutting down.
>$
```
