/*
  Gregory Mann
  COSC 439
  netp 3 Server 
  The Server part of project 3
*/

import java.io.*;
import java.net.*;
import java.util.Scanner;
import java.util.HashSet;
import java.util.NoSuchElementException;
import java.util.Base64;
import java.lang.Thread;
import java.lang.Math.*;
import java.math.BigInteger;

public class gmann1_TCPServer {
  public static final int    DEFAULT_PORT = 55556;
  public static final String DEFAULT_HOST = "localhost";
  public static final String    DEFAULT_N = "55555";
  public static final String    DEFAULT_G = "12345";
  public static final String    CHAT_FILE = "gmann1_chat.txt";
  private static HashSet<Client>  clients = new HashSet<>();
  private static int      numberOfClients = 0;

  // Functions for command line input
  // ***************************************************************************

  // Goes though commandline arguments 1 by 1 to find the corresponding match.
  private static String argParse(String[] args, String option) {
    boolean found = false;
    
    for (String s: args) {
      if (found) return s;
      if (option.equals(s)) found = true;
    }
    
    return "";
  }

  // Get the port from the command line or return the default value
  private static int getPort(String[] args) {
    String val = argParse(args, "-p");
    return (val.length() == 0) ? DEFAULT_PORT : Integer.parseInt(val);
  }

  // Get N from the command line or return the default value
  private static BigInteger getN(String[] args) {
    String val = argParse(args, "-n");
    return (val.length() == 0) ? new BigInteger(DEFAULT_N, 10) : new BigInteger(val, 10);
  }

  // Get G from the command line or return the default value
  private static BigInteger getG(String[] args) {
    String val = argParse(args, "-g");
    return (val.length() == 0) ? new BigInteger(DEFAULT_G, 10) : new BigInteger(val, 10);
  }

  // Returns a random number ranging from min to max
  private static int randomRange(int min, int max) {
    int range = (max - min) + 1;     
    return (int)(Math.random() * range) + min;
  }

  // Generate a PK
  private static BigInteger getPk() {
    return new BigInteger(new Integer(randomRange(0, Integer.MAX_VALUE -1)).toString(), 10);
  }

  // ***************************************************************************

  // A class that contains and generates parts of the key along with methods for using the key.
  private static class EncryptionKey {
    public BigInteger   g = null;
    public BigInteger   n = null;
    public BigInteger   x = null;
    public BigInteger   y = null;
    private BigInteger pk = null;
    private byte sharedPk = 0;

    public EncryptionKey(BigInteger g, BigInteger n, BigInteger pk) {
      this.g = g;
      this.n = n;
      this.pk = pk;
      this.x = g.modPow(pk, n);
    }

    // Generate the shared key
    public void genSharedKey() {
      sharedPk = (byte)(y.modPow(pk, n)).intValue();
    }

    // Return the source xor'ed with the key
    private byte[] cipher(byte[] source) {
      byte[] ret = new byte[source.length];
      
      for (int i = 0; i < source.length; i++)
        ret[i] = (byte)((int)source[i] ^ (int)sharedPk);
      
      return ret;
    }

    // Returns a string thats the encrypted message in base64 encoding
    public String encrypt(String message) {
      byte[] m = message.getBytes();
      byte[] e = cipher(m);
      String b = Base64.getEncoder().encodeToString(e);
      return b;
    }

    // Returns a string the original string from a message message in base64 encoding
    public String decrypt(String message) {
      byte[] e = Base64.getDecoder().decode(message);
      return new String(cipher(e));
    }
  }

  // Preforms the Server side of the hellmann key exchange
  private static void hellmannExchange(Client client) {
    client.out.println(client.key.g.toString());
    client.out.println(client.key.n.toString());
    client.out.println(client.key.x.toString());
    
    client.key.y = new BigInteger(client.in.nextLine(), 10);
    
    client.key.genSharedKey();
  }

  // A class containing information relating to a connected client
  public static class Client {
    String   username = "";
    Socket connection = null;
    Scanner        in = null;
    PrintStream   out = null;
    EncryptionKey key = null;
    
    public Client(Socket connection, EncryptionKey key) throws IOException {
      this.connection = connection;
      in = new Scanner(new InputStreamReader(connection.getInputStream()));
      out = new PrintStream(connection.getOutputStream());
      this.key = key;
    }
  }

  // Manages the number of when one disconnects and maybe deleates the chat file
  private static void clientDissconnected() {
    numberOfClients--;
    
    if (numberOfClients == 0) {
      File file = new File(CHAT_FILE);
      file.delete();
    }
  }

  // Manages the number of when one connects and maybe creates the chat file
  private static void clientConnected() {
    numberOfClients++;

    if (numberOfClients == 1) {
      try {
        File file = new File(CHAT_FILE);
        file.createNewFile();
      } catch (IOException E) {
        System.err.println("Failed to create chat file.");
      }
    }
  }

  // Writes a message to the chat file ensuring synchronization
  private synchronized static void writeToFile(String str) {
    try {
      FileWriter file = new FileWriter(CHAT_FILE, true);
      file.append(str + "\n");
      file.close();
    } catch (IOException E) {
      System.err.println("Failed to write to chat file.");
    }
  }

  // Sends the contents of the chat file to the user
  private static void sendChatTo(Client client) {
    try {
      Scanner file = new Scanner(new File(CHAT_FILE));
      String message = "";

      while (true) {
        try {
          client.out.println(client.key.encrypt(file.nextLine()));
        } catch (NoSuchElementException E) {
          break;
        }
      }
      file.close();
    } catch (IOException E) {
      System.err.println("Failed to read from chat file.");
    }
  }

  // Sends a message from a client to all other clients
  private static void broadcast(Client sender, String message) {
    String userMessage = sender.username + ": " + message;
    System.out.println(userMessage);
    writeToFile(userMessage);
    for (Client client: clients) {
      if (client != sender)
        client.out.println(client.key.encrypt(userMessage));
    }
  }
  
  // Code to run when a client connects
  public static void handleClient(Client client) {
    hellmannExchange(client);
    client.username = client.key.decrypt(client.in.nextLine());
    clientConnected();
    sendChatTo(client);
    broadcast(client, "has connected.");

    String message = "";

    while (true) {
      try {
        message = client.key.decrypt(client.in.nextLine());
        if (message.equals("DONE")) {
          broadcast(client, "has disconnected.");        
          break;
        }
        broadcast(client, message);
      } catch (NoSuchElementException E) {
        broadcast(client, "has disconnected.");        
        break;
      }
    }
    clientDissconnected();
  }

  public static void main(String[] args) {
    try {
      ServerSocket server = new ServerSocket(getPort(args));

      // Main loop for creating thread for clients
      while (true) {
        EncryptionKey k = new EncryptionKey(getG(args), getN(args), getPk());
        Client client = new Client(server.accept(), k);
        clients.add(client);
        new Thread(() -> { handleClient(client); }).start();
      }
    } catch (IOException E) {
      System.err.println("An IO Error has occured.");
    }
  }
}
