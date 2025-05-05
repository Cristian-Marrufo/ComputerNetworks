#include "time_server.h"

int main()
{
   initializeServer();
   return 0;
}

void initializeServer()
{
   int socketFileDescriptor;
   char rcvBuffer[MAX_BUFFER_SIZE];
   struct sockaddr_in serverAddress, clientAddress;

   memset(&serverAddress, 0, sizeof(serverAddress));
   memset(&clientAddress, 0, sizeof(clientAddress));

   socketFileDescriptor = socket(AF_INET, SOCK_DGRAM, 0);

   if(socketFileDescriptor < 0)
   {
      perror("Socket Creation Failed. Exiting Program.\n");
      exit(EXIT_FAILURE);
   }

   serverAddress.sin_family = AF_INET;
   serverAddress.sin_addr.s_addr = INADDR_ANY;
   serverAddress.sin_port = htons(SERVER_PORT);

   int bindResult = bind(socketFileDescriptor, 
               (const struct sockaddr *) &serverAddress, sizeof(serverAddress));
   
   if(bindResult < 0)
   {
      perror("Socket Binding Failed. Exiting Program.\n");
      exit(EXIT_FAILURE);
   }

   socklen_t lenClientAddress = sizeof(clientAddress);
   int rcvBytes;

   printf("Server is listening on port %d\n", SERVER_PORT);

   while(1)
   {
      rcvBytes = recvfrom(socketFileDescriptor, (char *)rcvBuffer, 
                MAX_BUFFER_SIZE, MSG_WAITALL, (struct sockaddr *)&clientAddress, 
                                                             &lenClientAddress);
      rcvBuffer[rcvBytes] = '\0';

      printf("Message from client: %s\n", rcvBuffer);

      if(strcmp(rcvBuffer, "time\r\n") == 0)
      {
         time_t currentTime = time(NULL);
         char response[MAX_BUFFER_SIZE];
         snprintf(response, MAX_BUFFER_SIZE, "%ld\n", currentTime);

          sendto(socketFileDescriptor, (const char *)response, strlen(response), 
                  0, (const struct sockaddr *)&clientAddress, lenClientAddress);
         
         printf("Sent time to client: %s\n", response);
      }
   }

   close(socketFileDescriptor);

   printf("Server socket closed.\n");

   return;

}

