/*
  Gregory Mann
  COSC 439
  netp 3 Server 
  The Client part of project 3
*/

import java.io.*;
import java.net.*;
import java.util.Scanner;
import java.util.NoSuchElementException;
import java.lang.Thread;
import java.util.Base64;
import java.lang.Math.*;
import java.math.BigInteger;

public class gmann1_TCPClient {
  public static final int DEFAULT_PORT = 55556;
  public static final String DEFAULT_HOST = "localhost";
  private static EncryptionKey key = null;


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

  // Get the hostname from the command line or return the default value
  private static String getHost(String[] args) {
    String val = argParse(args, "-h");
    return (val.length() == 0) ? DEFAULT_HOST : val;
  }

  // Get the port from the command line or return the default value
  private static int getPort(String[] args) {
    String val = argParse(args, "-p");
    return (val.length() == 0) ? DEFAULT_PORT : Integer.parseInt(val);

  }
  // Get the username from the command line or return the default value
  private static String getUsername(String[] args) {
    return argParse(args, "-u");
  }

  // Returns a random number ranging from min to max
  private static int randomRange(int min, int max) {
    int range = (max - min) + 1;
    return (int)(Math.random() * range) + min;
  }

  // Generate a PK
  private static BigInteger getPk() {
    return new BigInteger(new Integer(randomRange(0, Integer.MAX_VALUE -1)).toString());
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

  // Preforms the client side of the hellmann key exchange
  private static EncryptionKey hellmannExchange(Scanner in, PrintStream out) {
    BigInteger g = new BigInteger(in.nextLine(), 10);
    BigInteger n = new BigInteger(in.nextLine(), 10);
    BigInteger y = new BigInteger(in.nextLine(), 10);

    EncryptionKey key = new EncryptionKey(g, n, getPk());

    key.y = y;
    
    out.println(key.x);
    
    key.genSharedKey();

    return key;
  }

  // Starts a thread that displays incomming messages from the server
  public static void startDisplay(Scanner in) {
    new Thread(() -> {
        String line = null;
        
        while (true) {
          try {
            line = in.nextLine();
            System.out.println(key.decrypt(line));
          } catch (NoSuchElementException E) {
            break;
          }
        }
    }).start();
  }
  
  public static void main(String[] args) {
    Socket       user = null;
    Scanner        in = null;
    PrintStream   out = null;
    Scanner       kbd = null;

    try {
      int portNumber = getPort(args);
      String hostName = getHost(args);
      
      user = new Socket(hostName, portNumber);
      in   = new Scanner(new InputStreamReader(user.getInputStream()));
      out  = new PrintStream(user.getOutputStream());
      kbd  = new Scanner(System.in);
      key  = hellmannExchange(in, out);
      
      String username = getUsername(args);
      
      // Ask the user for a username before continuing.
      while (username.equals("")) {
        System.out.println("Enter a username.");
        username = kbd.nextLine();
      }

      out.println(key.encrypt(username));

      startDisplay(in);

      String message = "";

      // Send all userinput to the server.
      while (true) {
        message = kbd.nextLine();
        out.println(key.encrypt(message));
        if (message.equals("DONE")) break;
      }
    } catch (IOException E) {
      System.err.println("An IO Error has occured.");
    } finally {
      System.exit(0);
    }
  }
}
