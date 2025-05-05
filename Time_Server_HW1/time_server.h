#ifndef TIME_SERVER_H
#define TIME_SERVER_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <signal.h>
#include <time.h>

#define SERVER_PORT 8888
#define MAX_BUFFER_SIZE 1024

void initializeServer();

#endif // TIME_SERVER_H