#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <signal.h>

// For Windows:
// #define _WIN32_WINNT 0x501 for windows xp and above
// #include <winsock2.h>
// #include <ws2tcpip.h>
// #pragma comment(lib, "ws2_32.lib") to link the library


#define SERVER_PORT 8888
#define MAX_BUFFER_SIZE 1024  // Buffer Size = 1KBytes




void initialize_and_run_server()
{

	/*
		This function initializes and sets up
		the UDP server socket on a specified
		port (and IP address).

	*/


	// -------------------------------------- (1) Initialize Variables ------------------------------------------------------

	
	// Declare and initialize variables:
	//
	int server_socket_file_descriptor; // handle for the server socket object
	char rcv_buffer[MAX_BUFFER_SIZE]; // Buffer to store the message from client
	struct sockaddr_in server_address,client_address; // Socket Address objects for the server and client

	// Initialize the server and client address objects' 
	// member fields with zero (0) values
	//
	memset(&server_address,0,sizeof(server_address));
	memset(&client_address,0,sizeof(client_address));



	// ---------------------------------- (2) Create the Socket ----------------------------------------------------------

	// Create socket. If creation fails,
	// print error and exit program:
	//
	server_socket_file_descriptor = socket(AF_INET,SOCK_DGRAM,0); // namespace, style of socket, protocol
	
	// If the socket creation failed, print error
	// and exit program:
	if(server_socket_file_descriptor < 0)
	{
		perror("Socket Creation Failed. Exiting Program.\n");
		exit(EXIT_FAILURE);
	}

	

	// ----------------------------- (3) Bind Socket  --------------------------------------------------------
	


	// Set server socket address properties before 
	// binding the socket to (address,port):
	//
	server_address.sin_family = AF_INET; // IPV4
	server_address.sin_addr.s_addr = INADDR_ANY; // IP Address this socket will be bound to
	server_address.sin_port = htons(SERVER_PORT); // Port number this socket will be bound to 


	// Bind the server socket to the
	// server_address object:
	//
	int bind_result = bind(server_socket_file_descriptor,(const struct sockaddr*) &server_address, sizeof(server_address));

	// Exit if binding failed:
	if(bind_result < 0)
	{
		perror("Socket Binding Failed. Exiting Program.\n");
		exit(EXIT_FAILURE);
	}



	// ------------------------------------ (4) Handle A Client Request -------------------------------


	// Variable to store the length of 
	// the client's address:
	int len_client_address;

	// Variable to store the length of 
	// the message received from the 
	// client:
	int rcvd_bytes;


	// Print a confirmation that the server is listening:
	printf("Server is listening on port %d\n",SERVER_PORT);

	// Read the message sent by the client:
	rcvd_bytes = recvfrom(server_socket_file_descriptor,(char*)rcv_buffer,MAX_BUFFER_SIZE,MSG_WAITALL,(struct sockaddr *) &client_address,&len_client_address);
	rcv_buffer[rcvd_bytes] = '\0'; // null-terminating the received string


	// Print Client Message:
	printf("Message from Client => %s\n",rcv_buffer);


	// Prepare server reply:
	char* server_reply = "Server Says: Hello World!!!\n";

	// Send message to client:
	sendto(server_socket_file_descriptor, (const char *)server_reply, strlen(server_reply), 0, (const struct sockaddr *) &client_address, len_client_address);
	
	// Print confirmation:
	printf("Message sent to client.\n");


	// Close socket:
	close(server_socket_file_descriptor);


	// Announce exit:
	printf("Server Socket Close.\n");


	// Return to main:
	return;


}



int main()
{

	// Initialize server:
	initialize_and_run_server();


	return 0;
}




