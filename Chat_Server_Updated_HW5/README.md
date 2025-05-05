## CS460 Computer Networks: **Homework 5**

# Files Included
1. server.py
2. client.py

# Running the Code:
1. To run the server use "python3 server.py"
2. To run the client use "python3 client.py"
3. When prompted, enter the server's IP address (0.0.0.0)

4. Follow the on-screen prompts:
   - Enter your user id
   - Choose to create or join a chat room
   - Start chatting
   - To test file transfer, type commands such as:
       * For file listing: "@RecipientUser -ls" or "@RecipientUser@YourUser -ls [transaction_id]\r\n\r\n"
       * For file request: "@RecipientUser@YourUser -f filename transaction_id\r\n\r\n"
5. To disconnect, type "CLOSE"