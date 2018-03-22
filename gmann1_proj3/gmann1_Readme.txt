Greogry Mann
Project 3
Time: Too long

# Before running the program
First check the Java version:
```
>$ java -version
openjdk version "1.8.0_161"
OpenJDK Runtime Environment (build 1.8.0_161-b14)
OpenJDK 64-Bit Server VM (build 25.161-b14, mixed mode)
```

If the version is less than "1.8": Upgrade your java version.

# Running the program
Assuming the right Java version
Compile the Server and the Client:
```
>$ javac gmann1_TCPServer.java gmann1_TCPClient.java
```

Running the server:
```
>$ java gmann1_TCPServer
```

Connecting with the client:
```
>$ java gmann1_TCPClient
```

The Server program can take the following optional arguments in any order:
-p <Port number>
-n <N value for the Diffie Hellman key exchange>
-g <G value for the Diffie Hellman key exchange>
```
>$ java gmann1_TCPServer -p 55556 -n 55555 -g 12345
```

The Client program can take the following optional arguments in any order:
-p <Port Number>
-h <Host name>
-u <User name>
```
>$ java gmann1_TCPClient -u Gregory -p 55556 -h localhost
```
