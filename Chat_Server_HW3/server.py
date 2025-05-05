import socket
import select

def main():
   serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   serverSocket.bind(("", 8181))

   serverSocket.listen(5)
   print("Server listening on port 8181")

   socketList = [serverSocket]
   clients = {}
   chatRooms = {}

   while True:
      readSockets, _, exceptionSockets = select.select(socketList, [], 
                                                       socketList)
      
      for notifiedSocket in readSockets:
         if notifiedSocket == serverSocket:
            clientSocket, clientAddress = serverSocket.accept()
            socketList.append(clientSocket)

            clients[clientSocket] = {
               "address": clientAddress,
               "username": None,
               "state": "username",
               "room": None
            }
         
            welcomeMessage = ("Welcome to the chat server!\n"
                              "Please enter your username or type 'CLOSE' to " 
                              "disconnect:")
            clientSocket.send(welcomeMessage.encode())

         else:
            try: 
               message = notifiedSocket.recv(1024).decode().strip()
            except Exception:
               message = ''
            
            if not message:
               disconnectClient(notifiedSocket, socketList, clients, chatRooms)
               continue

            if message == "CLOSE":
               disconnectClient(notifiedSocket, socketList, clients, chatRooms)
               continue
         
            clientInfo = clients[notifiedSocket]
            state = clientInfo["state"]

            if state == "username":
               clientInfo["username"] = message
               clientInfo["state"] = "roomSelect"

               prompt = (f"Hello {message}!\nSelect an option:\n"
                         "Type 1 to create and join a new chat room.\n"
                         "Type 2 to join an existing chat room.\n"
                         "Type 'CLOSE' to exit.")
               notifiedSocket.send(prompt.encode())

            elif state == "roomSelect":
               if message == "1":
                  clientInfo["state"] = "newRoom"
                  notifiedSocket.send("Enter new chat room name:".encode())
               
               elif message == "2":
                  if len(chatRooms) == 0:
                     noChatRooms = ("No chat rooms available. "
                                    "Please create a new one.")
                     notifiedSocket.send(noChatRooms.encode())
                  
                  else:
                     rooms = "\n".join(chatRooms.keys())
                     roomList = ("Available chat rooms:\n" + rooms + 
                                 "\nEnter the chat room name to join:")
                     clientInfo["state"] = "joinRoom"
                     notifiedSocket.send(roomList.encode())
               
               else:
                  invalidOptions = ("Invalid option. " 
                                    "Type 1, 2, or 'CLOSE'.")
                  notifiedSocket.send(invalidOptions.encode())
            
            elif state == "newRoom":
               roomName = message

               if roomName in chatRooms:
                  chatRoomNameExists = ("Chat room already exists. " 
                                        "Enter a different name:")
                  notifiedSocket.send(chatRoomNameExists.encode())
               
               else:
                  chatRooms[roomName] = [notifiedSocket]
                  clientInfo["room"] = roomName
                  clientInfo["state"] = "chatting"

                  roomCreated = ("You have created and joined the chat room "
                                 f"{roomName}.\n")
                  notifiedSocket.send(roomCreated.encode())
            
            elif state == "joinRoom":
               roomName = message

               if roomName in chatRooms:
                  chatRooms[roomName].append(notifiedSocket)
                  clientInfo["room"] = roomName
                  clientInfo["state"] = "chatting"

                  joinedRoom = (f"Joined chat room {roomName}.\n")
                  notifiedSocket.send(joinedRoom.encode())

                  broadcastMessage = (f"\n{clientInfo['username']} has joined "
                                      "the chat room.\n")
                  broadcast(notifiedSocket, chatRooms[roomName], 
                            broadcastMessage)
               
               else:
                  chatRoomDoesNotExist = ("Chat room does not exist. "
                                          "Please try again.")
                  notifiedSocket.send(chatRoomDoesNotExist.encode())
            
            elif state == "chatting":
               roomName = clientInfo["room"]

               fullMessage = (f"{clientInfo['username']} >> {message}")

               for client in chatRooms.get(roomName, []):
                  if client != notifiedSocket:
                     try:
                        client.send(fullMessage.encode())
                     except Exception:
                        disconnectClient(client, socketList, clients, chatRooms)
            
            else:
               notifiedSocket.send("Invalid state.\n".encode())
         
         for notifiedSocket in exceptionSockets:
            disconnectClient(notifiedSocket, socketList, clients, chatRooms)


def broadcast(sender, room, message):
   for client in room:
      if client != sender:
         try:
            client.send(message.encode())
         except Exception:
            pass

def disconnectClient(clientSocket, socketList, clients, chatRooms):
   if clientSocket in clients:
      room = clients[clientSocket]["room"]

      if room and room in chatRooms and clientSocket in chatRooms[room]:
         chatRooms[room].remove(clientSocket)
         username = clients[clientSocket]["username"]

         leaveMessage = (f"\n{username} has left the chat room.\n")

         for client in chatRooms[room]:
            try:
               client.send(leaveMessage.encode())
            except Exception:
               pass
         
      if clientSocket in socketList:
         socketList.remove(clientSocket)
      
      clientSocket.close()
      del clients[clientSocket]


if __name__ == "__main__":
   main()