import socket 
import select
import sys

def main():
   if len(sys.argv) < 2:
      print("Usage: python3 client.py <serverIP>\n")
      return

   serverIP = sys.argv[1]
   serverAddress = (serverIP, 8181)

   clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

   try:
      clientSocket.connect(serverAddress)
   except Exception as e:
      print("Unable to connect to server:", e)
      return

   print("\nConnected to the chat server. You can now send messages.\n")

   running = True
   try:
      while running:
         readList, _, _ = select.select([clientSocket, sys.stdin], [], [])

         for source in readList:
            if source == clientSocket:
               try:
                  message = clientSocket.recv(1024).decode()
               except Exception:
                  print("Error receiving message.\n")
                  running = False
                  break
         
               if not message:
                  print("Connection closed.\n")
                  running = False
                  break

               print(message)

            else:
               userInput = sys.stdin.readline()

               if userInput:
                  message = userInput.strip()

                  try:
                     clientSocket.send(message.encode())
                  except Exception:
                     print("Error sending message.\n")
                     running = False
                     break
            
                  if message == "CLOSE":
                     print("Disconnecting from server.\n")
                     running = False
                     break

   finally:               
      clientSocket.close()
      print("Socket closed.\n")

if __name__ == "__main__":
   main()