'''
	
	CS460(Spring-2025)	
	Homework-3: Server program for the text-based 
						 chat application. Server is 
                         implemeneted as a Python class.
	Author:
		Nazmul(mh2752@nau.edu)

'''
import socket
import threading
import re
import sys

# -------------------------------------- Server Class -----------------------------------------------

class ChatServer:


    # -------------------- Class Private Member Variables ----------------------

    # A dictinary for storing chat room names and the list of 
    # 2-tuples of active participants' sockets and user ids:
    __dictionary_chat_room_participants = None # Dictionary format: key="chatroom_name",value=[(participant_1_socket,participant_1_user_id),.....,(participant_n_socket,participant_n_user_id)]

    # TCP port number for the server to listen 
    # for incoming client requests:
    __server_port_number = None

    # IP address of the server:
    __server_ip_address = None

    # Handle for server socket:
    __server_socket = None

    # Flag to control the server's 
    # running status:
    __server_keep_running = None

    # Maximum number of clients to 
    # be allowed to wait in the 
    # buffer by the server socket:
    __MAX_CLIENTS = None

    # Maximum length of the buffer 
    # for receiving messages 
    # from client:
    __MAX_BUFFER_LENGTH = None 

    __user_connections = None
    __user_connections_lock = None

    __PATTERN_LS_CMD = None
    __PATTERN_LS_REQ = None
    __PATTERN_FILE_REQ = None
    __PATTERN_FILE_RESP = None

    # ------------------------------------ Class Initializer/Constructor ----------------------------
    def __init__(self):
        
        # Print dialog:
        print("Initializing chat server...")

        # Initialize class member variables:
        try:
            self.__dictionary_chat_room_participants = {}
            self.__server_port_number = 8181
            self.__server_ip_address = "0.0.0.0"
            self.__server_keep_running = True
            self.__MAX_CLIENTS = 100
            self.__MAX_BUFFER_LENGTH = 1024

            self.__user_connections = {}
            self.__user_connections_lock = threading.Lock()

            # Create socket:
            self.__server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

            # Set server socket to be non-blocking:
            self.__server_socket.setblocking(False)

            # Set socket option to keep it alive:
            self.__server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,1)

            # Bind socket to the address and port:
            self.__server_socket.bind((self.__server_ip_address,self.__server_port_number))

            self.__PATTERN_LS_CMD   = re.compile(r'^@(\w+)\s+-ls$')
            self.__PATTERN_LS_REQ   = re.compile(r'^@(\w+)@(\w+)\s+-ls\s+(\S+)\r\n\r\n$')
            self.__PATTERN_FILE_REQ = re.compile(r'^@(\w+)@(\w+)\s+-f\s+(\S+)\s+(\S+)\r\n\r\n$')
            self.__PATTERN_FILE_RESP= re.compile(r'^@(\w+)@(\w+)\s+-f\s+(\S+)\s+(\S+)\r\n(.+?)\r\n(\d+)\r\n(.+?)\r\nENDFILE\r\n\r\n$', re.DOTALL)           

            # Print confirmation dialog:
            print("Done initializing chat server. Server is ready to run...")


        except Exception as e:

            # Print dialog:
            print("[Exception] Caught exception during server initialization. Details: ",e)

            # If not None, close server socket:
            if self.__server_socket != None:
                
                # Close socket:
                self.__server_socket.close()

                # Print confirmation:
                print("Closed server socket.")
            
            # Exit program with code -1:
            print("Exiting program...")
            sys.exit(-1)


    # ------------------------------------ Class Private Member Functions --------------------------
    
    def __mainThreadedLoop(self):
        print("Chat server running on TCP port ", self.__server_port_number)
        self.__server_socket.listen(self.__MAX_CLIENTS)

        try:
            while self.__server_keep_running:
                try:
                    client_socket, client_addr = self.__server_socket.accept()
                    print("New client connected from ", client_addr)
                    client_socket.setblocking(True)

                    t = threading.Thread(target=self.__handleClientSession, args=(client_socket, client_addr))
                    t.daemon = True
                    t.start()
                except BlockingIOError:
                    continue
        except KeyboardInterrupt:
            self.__signal_handler()
        finally:
            self.__doPostStopCleanup()

    def __handleClientSession(self, client_socket, client_addr):
        try:
            welcome_message = "Welcome! Please enter your user id to continue."
            self.__sendMessageToAClient(client_socket, welcome_message)

            user_id = self.__readMessageFromSocket(client_socket)
            if not self.__isValidUserId(user_id):
                self.__sendMessageToAClient(client_socket, "Invalid user id. Closing connection.")
                client_socket.close()
                return

            join_instruction = f"Hi, {user_id}! Enter 1 or 2 for - (1) Create and Join a Chat Room (2) Join an Existing Chat Room."
            self.__sendMessageToAClient(client_socket, join_instruction)

            choice = self.__readMessageFromSocket(client_socket)
            if not self.__isValidJoinChoice(choice):
                self.__sendMessageToAClient(client_socket, "Invalid join choice. Closing connection.")
                client_socket.close()
                return

            self.__sendMessageToAClient(client_socket, "Enter a chat room name to create or join.")
            chat_room_name = self.__readMessageFromSocket(client_socket)
            if not self.__isChatRoomNameValid(chat_room_name):
                self.__sendMessageToAClient(client_socket, "Invalid chat room name. Closing connection.")
                client_socket.close()
                return

            if choice == "1":
                if self.__doesChosenChatroomExist(chat_room_name):
                    self.__sendMessageToAClient(client_socket, "A chat room with this name already exists. Closing connection.")
                    client_socket.close()
                    return
                else:
                    self.__dictionary_chat_room_participants[chat_room_name] = [(client_socket, user_id)]
            else:
                if not self.__IsAnyChatroomAvailable():
                    self.__dictionary_chat_room_participants[chat_room_name] = [(client_socket, user_id)]
                else:
                    if not self.__doesChosenChatroomExist(chat_room_name):
                        self.__sendMessageToAClient(client_socket, "Chosen chat room not available. Closing connection.")
                        client_socket.close()
                        return
                    else:
                        self.__dictionary_chat_room_participants[chat_room_name].append((client_socket, user_id))

            confirmation_message = f"Successfully joined chat room {chat_room_name}. Happy chatting!"
            self.__sendMessageToAClient(client_socket, confirmation_message)

            with self.__user_connections_lock:
                self.__user_connections[user_id] = (client_socket, chat_room_name)

            while True:
                client_message = self.__readMessageFromSocket(client_socket)
                if client_message == "" or client_message is None:
                    break

                if client_message.strip() == "CLOSE":
                    self.__sendMessageToAClient(client_socket, "Goodbye!")
                    break

                if self.__checkAndHandleFileCommands(client_socket, user_id, client_message):
                    continue
                else:
                    self.__relayMessageToChatroomParticipants(client_socket, client_message, user_id)

            self.__initiateCloseSequence(client_socket, user_id, chat_room_name)

        except Exception as e:
            print("[Exception] in client session: ", e)
            try:
                if client_socket:
                    client_socket.close()
            except:
                pass
        finally:
            pass 

    def __checkAndHandleFileCommands(self, client_socket, sender_user_id, message):

        m_simple_ls = self.__PATTERN_LS_CMD.match(message)
        if m_simple_ls:
            target_user = m_simple_ls.group(1)
            self.__forwardPrivateMessage(client_socket, sender_user_id, target_user, message, "N/A")
            return True

        m_ls_req = self.__PATTERN_LS_REQ.match(message)
        if m_ls_req:
            recv_user, send_user, trans_id = m_ls_req.group(1,2,3)
            if recv_user and send_user:
                self.__forwardPrivateMessage(client_socket, send_user, recv_user, message, trans_id)
            return True

        m_file_req = self.__PATTERN_FILE_REQ.match(message)
        if m_file_req:
            recv_user, send_user, filename, trans_id = m_file_req.group(1,2,3,4)
            self.__forwardPrivateMessage(client_socket, send_user, recv_user, message, trans_id)
            return True

        m_file_resp = self.__PATTERN_FILE_RESP.match(message)
        if m_file_resp:
            recv_user, send_user, filename, trans_id, file_type, file_len, file_bytes = m_file_resp.group(1,2,3,4,5,6,7)
            if recv_user and send_user:
                self.__forwardPrivateMessage(client_socket, send_user, recv_user, message, trans_id)
            return True

        return False
    
    def __forwardPrivateMessage(self, client_socket, actual_sender, target_user, msg, trans_id):
        self.__sendMessageToAClient(client_socket, msg)
        with self.__user_connections_lock:
            if target_user in self.__user_connections:
                (t_sock, _) = self.__user_connections[target_user]
                self.__sendMessageToAClient(t_sock, msg)
            else:
                error_msg = self.format_error(trans_id, "Recipient not found")
                self.__sendMessageToAClient(client_socket, error_msg)

    def format_error(self, transaction_id, details=""):
        return f"!!!ERROR!!!{transaction_id}\r\n{details}\r\n\r\n"

    def __readMessageFromSocket(self,source_socket):
        try:
            read_message = source_socket.recv(self.__MAX_BUFFER_LENGTH)
            if not read_message:
                return None
            return read_message.decode('UTF-8').strip()
        except Exception as e:
            print("[Exception] Error in reading message from socket. Details: ", e)
            return None

    def __isValidUserId(self,user_id):

        if not user_id:
            return False
        if user_id.strip() == "":
            return False
        return True

    def __isValidJoinChoice(self,join_choice):

        return join_choice in ["1","2"]
               
    def __IsAnyChatroomAvailable(self):

        return len(self.__dictionary_chat_room_participants) > 0
            
    def __isChatRoomNameValid(self,chosen_chat_room):

        if not chosen_chat_room:
            return False
        if chosen_chat_room.strip() == "":
            return False
        return True

    def __doesChosenChatroomExist(self,chosen_chat_room):

        return chosen_chat_room in self.__dictionary_chat_room_participants

    def __relayMessageToChatroomParticipants(self, client_socket, client_message, sender_user_id):
        try:
            client_chat_room_name = None
            for room_name, participants in self.__dictionary_chat_room_participants.items():
                for (sock, uid) in participants:
                    if sock == client_socket:
                        client_chat_room_name = room_name
                        break
                if client_chat_room_name is not None:
                    break

            if not client_chat_room_name:
                self.__sendMessageToAClient(client_socket, "You are not in a chat room.\n")
                return

            relay_message = sender_user_id + ": " + client_message

            list_chat_room_member_tuples = self.__dictionary_chat_room_participants[client_chat_room_name]
            for (sock, uid) in list_chat_room_member_tuples:
                if sock != client_socket:
                    self.__sendMessageToAClient(sock, relay_message)
            self.__sendMessageToAClient(client_socket, relay_message)
        except Exception as e:
            print("[Exception] in __relayMessageToChatroomParticipants: ", e)

    def __initiateCloseSequence(self, client_socket, user_id, chat_room_name):
        try:
            if chat_room_name in self.__dictionary_chat_room_participants:
                self.__dictionary_chat_room_participants[chat_room_name] = [
                    (s,u) for (s,u) in self.__dictionary_chat_room_participants[chat_room_name] 
                    if s != client_socket
                ]

            with self.__user_connections_lock:
                if user_id in self.__user_connections:
                    del self.__user_connections[user_id]

            client_socket.close()
            print(f"User {user_id} has left chat room {chat_room_name}")
        except Exception as e:
            print("[Exception] in __initiateCloseSequence: ", e)

    def __signal_handler(self):

        self.__server_keep_running = False
        print("\nCtrl+C pressed. Chat server has been shut down.")

    def __doPostStopCleanup(self):

        try:
            if self.__server_socket:
                self.__server_socket.close()
            del self.__dictionary_chat_room_participants
        except Exception as e:
            print("[Exception] Caught exception during post stop cleaning. Details: ",e)
            sys.exit(-1)

    def __sendMessageToAClient(self,client_socket,str_message_to_send):

        encoded_message = str_message_to_send.encode('UTF-8')
        total_data_sent = 0
        while(total_data_sent < len(encoded_message)):
            try:
                number_of_bytes_sent = client_socket.send(encoded_message[total_data_sent:])
                if(number_of_bytes_sent == 0):
                    raise Exception("Unable to send data. Connection closed by remote peer.")
                total_data_sent += number_of_bytes_sent
            except BlockingIOError:
                continue 

    

    # ------------------------------------ Class Public Member Functions ---------------------------
    def run_server(self):

        # Show confirmation dialog:
        print("Running chat server program...")

        # -------- Necessary Function Calls ------------
        #self.__mainEventHandler()

        self.__mainThreadedLoop()

        

# *********************************** Main Function **************************************************
def main():

    # Create a ChatServer object:
    chat_server = ChatServer()

    # Start running the chat server:
    chat_server.run_server()


if __name__ == "__main__":
    main()