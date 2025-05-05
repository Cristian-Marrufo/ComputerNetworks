#ifndef ECHO_SERVER_H
#define ECHO_SERVER_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <signal.h>
#include <errno.h>

#define SERVER_PORT 8888
#define MAX_BUFFER_SIZE 1024
#define MAX_CLIENTS 5
#define PENDING_QUEUE 3

#endif // ECHO_SERVER_H