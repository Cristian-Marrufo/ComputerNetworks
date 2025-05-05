'''
	
	CS460(Spring-2025)	
	Homework-3: Client program for the text-based 
						 chat application.
	Author:
		Nazmul(mh2752@nau.edu)

'''

import socket
import threading
import sys
import os

HOSTED_FILES_DIR = "./hosted_files"
if not os.path.exists(HOSTED_FILES_DIR):
    os.makedirs(HOSTED_FILES_DIR)

# ----------------------------------------------------- Main Function ---------------------------------------------------
def main():
    print("Starting chat client...")

    server_ip = None
    server_ip = input("Enter chat server's IP address: ")
    server_port = 8181

    try:
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print(f"Connected to chat server at IP address = {server_ip} PORT# = {server_port}")

        listener_thread = threading.Thread(target=listen_for_server_messages, args=(client_socket,))
        listener_thread.daemon = True
        listener_thread.start()

        while True:
            user_input = sys.stdin.readline().strip()
            if user_input == "CLOSE":
                sendMessageToAClient(client_socket, user_input)
                client_socket.close()
                break
            else:
                sendMessageToAClient(client_socket, user_input + "\r\n")

    except Exception as e:
        print("[Exception] Caught exception in new approach: ", e)
        try:
            client_socket.close()
        except:
            pass
        sys.exit(-1)


# ------------------------------------------- Helper Function(s) ---------------------------------------------------------

def listen_for_server_messages(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("Disconnected from server.")
                break
            server_message = data.decode('UTF-8')
            if server_message.strip() == "":
                continue
            if server_message.startswith("@") and "-ls" in server_message:
                handle_ls_command(sock, server_message)
            elif server_message.startswith("@") and "-f" in server_message:
                handle_file_request(sock, server_message)
            else:
                print("\n>>> " + server_message.strip())
        except Exception as e:
            print("[Exception] in listen_for_server_messages: ", e)
            break

def handle_ls_command(sock, incoming_message):
    files = os.listdir(HOSTED_FILES_DIR)
    if not files:
        response = incoming_message + "\r\nNO_FILES\r\n\r\n"
    else:
        file_lines = []
        for fname in files:
            fpath = os.path.join(HOSTED_FILES_DIR, fname)
            if os.path.isfile(fpath):
                size = os.path.getsize(fpath)
                ext = fname.split('.')[-1].upper() if '.' in fname else "UNKNOWN"
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024*1024:
                    size_str = f"{size//1024}KB"
                else:
                    size_str = f"{size//(1024*1024)}MB"
                file_lines.append(f"{fname} {ext} {size_str}")
        file_listing = "\r\n".join(file_lines)
        response = incoming_message + "\r\n" + file_listing + "\r\n\r\n"
    sock.send(response.encode('UTF-8'))

def handle_file_request(sock, incoming_message):
    try:
        msg_stripped = incoming_message.strip()
        parts = msg_stripped.split()
        if len(parts) >= 4 and parts[1] == "-f":
            filename = parts[2]
            trans_id = parts[3] if len(parts) > 3 else "N/A"
            fpath = os.path.join(HOSTED_FILES_DIR, filename)
            if os.path.exists(fpath) and os.path.isfile(fpath):
                with open(fpath, "rb") as f:
                    file_bytes = f.read()
                ftype = filename.split('.')[-1].upper() if '.' in filename else "UNKNOWN"
                flen = len(file_bytes)
                file_hex = file_bytes.hex()
                header = parts[0]
                response = f"{header} -f {filename} {trans_id}\r\n{ftype}\r\n{flen}\r\n{file_hex}\r\nENDFILE\r\n\r\n"
                sock.send(response.encode('UTF-8'))
            else:
                error_resp = f"!!!ERROR!!!{trans_id}\r\nFile not found\r\n\r\n"
                sock.send(error_resp.encode('UTF-8'))
        else:
            print("\n>>> " + incoming_message.strip())
    except Exception as e:
        print("[Exception] in handle_file_request: ", e)

def sendMessageToAClient(client_socket,str_message_to_send):
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

# -------------------------------------------------- Run Main ----------------------------------------------------------
if __name__ == "__main__":
	main()







