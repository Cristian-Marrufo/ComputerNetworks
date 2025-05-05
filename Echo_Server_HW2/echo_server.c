#include "echo_server.h"

// Main function containing server logic
int main()
{
   // Initialize variables
   int serverFD, newSocket, clientSocket[MAX_CLIENTS], activity;
   int maxSocketDescriptor, socketDescriptor, inputRead;
   struct sockaddr_in serverAddress;
   int addressLength = sizeof(serverAddress);
   char buffer[MAX_BUFFER_SIZE];

   // Initialize address object
      // function: memset
   memset(&serverAddress, 0, sizeof(serverAddress));

   // Initialize client socket array
   for(int index = 0; index < MAX_CLIENTS; index++)
   {
      clientSocket[index] = 0;
   }

   // Create server socket, return error if failed
      // function: socket(domain, socket type, protocol)
      // domain: AF_INET (IPv4)
      // socket type: SOCK_STREAM (TCP)
      // protocol: 0 (default)
   if((serverFD = socket(AF_INET, SOCK_STREAM, 0)) == 0)
   {
      perror("Socket creation failed.\n");
      exit(EXIT_FAILURE);
   }

   // Set socket options to allow address reuse
      // function: setsockopt
   int option = 1;
   if(setsockopt(serverFD, SOL_SOCKET, SO_REUSEADDR, &option, 
                                                            sizeof(option)) < 0)
   {
      perror("Setsockopt failed.\n");
      exit(EXIT_FAILURE);
   }

   // Set server address properties
      // function: htons
      // sin_family: AF_INET (IPv4)
      // sin_addr.s_addr: INADDR_ANY (any address)
      // sin_port: SERVER_PORT (8888)
   serverAddress.sin_family = AF_INET;
   serverAddress.sin_addr.s_addr = INADDR_ANY;
   serverAddress.sin_port = htons(SERVER_PORT);

   // Bind socket to server address
      // function: bind
   if(bind(serverFD, (const struct sockaddr *) &serverAddress, 
                                                     sizeof(serverAddress)) < 0)
   {
      perror("Socket binding failed.\n");
      exit(EXIT_FAILURE);
   }

   // Set server to listen for incoming connections
      // function: listen
   if(listen(serverFD, PENDING_QUEUE) < 0)
   {
      perror("Listen failed.\n");
      exit(EXIT_FAILURE);
   }

   // Display server listening message
   printf("Server is listening on port %d\n", SERVER_PORT);

   // Initiate main server loop
   while(1)
   {
      // Initialize file descriptor set
         // function: FD_ZERO
      fd_set readFDs;
      FD_ZERO(&readFDs);

      // Add server socket and client sockets to file descriptor set
         // function: FD_SET
      FD_SET(serverFD, &readFDs);

      // Set max socket descriptor (server socket is the highest at first)
      maxSocketDescriptor = serverFD;

      // Add client sockets to file descriptor set and update max SD
      for(int index = 0; index < MAX_CLIENTS; index++)
      {
         // Assign current client socket descriptor
         socketDescriptor = clientSocket[index];

         // Add current socket descriptor to file descriptor set
            // function: FD_SET
         if(socketDescriptor > 0)
         {
            FD_SET(socketDescriptor, &readFDs);
         }

         // Update max socket descriptor if necessary
         if(socketDescriptor > maxSocketDescriptor)
         {
            maxSocketDescriptor = socketDescriptor;
         }
      }

      // Call select to wait for activity on sockets
         // function: select
      activity = select(maxSocketDescriptor + 1, &readFDs, NULL, NULL, NULL);
      // Check for error in select call
      if((activity < 0) && (errno != EINTR))
      {
         perror("Select failed.\n");
      }

      // Check for incoming connection on server socket
         // function: FD_ISSET
      if(FD_ISSET(serverFD, &readFDs))
      {
         // Accept incoming connection and check for error
            // function: accept
         if((newSocket = accept(serverFD, 
                                       (struct sockaddr *) &serverAddress, 
                                             (socklen_t *) &addressLength)) < 0)
         {
            perror("Accept failed.\n");
            exit(EXIT_FAILURE);
         }

         // Display connection information
            // function: inet_ntoa, ntohs
         printf("New Connection: Socket File Descriptor %d, IP %s, Port %d\n",
                                   newSocket, inet_ntoa(serverAddress.sin_addr), 
                                                 ntohs(serverAddress.sin_port));
         
         // Add new socket to client socket array
         for(int index = 0; index < MAX_CLIENTS; index++)
         {
            // Check for empty slot in client array
            if(clientSocket[index] == 0)
            {
               // Add new socket to client array
               clientSocket[index] = newSocket;

               // Display index of new socket in client array and break loop
               printf("New client socket added to clietn socket array at " 
                                                           "index %d\n", index);
               
               // Break loop after first empty slot found
               break;
            }
         }
      }

      // Check client sockets for incoming data
      for(int index = 0; index < MAX_CLIENTS; index++)
      {
         // Assign current client socket descriptor
         socketDescriptor = clientSocket[index];

         // Check for activity on current client socket descriptor
            // function: FD_ISSET
         if(FD_ISSET(socketDescriptor, &readFDs))
         {
            // Read incoming data and check for disconnection
               // function: read
            if((inputRead = read(socketDescriptor, buffer, 
                                                         MAX_BUFFER_SIZE)) == 0)
            {
               // If client disconnected display client information
                  // function: getpeername, inet_ntoa, ntohs
               getpeername(socketDescriptor, 
                                       (struct sockaddr *) &serverAddress, 
                                                   (socklen_t*) &addressLength);
               printf("Client Disconnected: IP %s, Port %d\n",
                                              inet_ntoa(serverAddress.sin_addr), 
                                                 ntohs(serverAddress.sin_port));
               
               // Close client socket and remove from client socket array
                  // function: close
               close(socketDescriptor);
               clientSocket[index] = 0;
            }

            // If client has not disconnected echo incoming data
            else
            {
               // Null-terminate incoming data
               buffer[inputRead] = '\0';

               // Echo back data read
                  // function: send
               send(socketDescriptor, buffer, strlen(buffer), 0);
            }
         }
      }
   }

   return 0;
}