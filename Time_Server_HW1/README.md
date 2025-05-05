## CS460 Computer Networks: **Homework 1**

# The directory includes the following
1. README.md
2. time_server.c
3. time_server.h
4. timeServer_mf

# Makefile: Compile the source code
To compile the program, run the following command in the server's terminal:
* make -f timeServer_mf

To clean the executable file, run the following command in the server's terminal:
* make -f timeServer_mf clean

# Time Server: Primary functions
To run the server, run the following command inside the server's directory:
* ./output

Once the server is running, the client is able to send the "time\r\n" request.
The Server will respond accordingly and output the number of seconds since the Epoch.

To stop the server, run the following command inside the server's directory:
* ctr + c