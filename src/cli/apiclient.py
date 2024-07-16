import socket
import subprocess
import os
import threading
from time import sleep

status_messages = {
    100: "The request has been processed",
    101: "The server is running",
    102: "The server is stoppped",


    200: "OK",
    201: "The server has started",
    202: "The server has been stopped",
    203: "Backup done",

    301: "The server name was not found",
    302: "There are no servers with backup enabled",
    
    401: "Unknown command",

    501: "The server could not be started",
    502: "The server could not be stopped",
    
}

class ApiClient:
    def __init__(self):
        self.stop_event = threading.Event()

    def send_command(self, command, server_name, mute=False):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(('127.0.0.1', 9198))
        except BaseException:
            print('Unable to connect to the daemon. The service may not be running.')
        client_socket.sendall(f"{command} {server_name}".encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        try:
            response = int(response)
        except BaseException:
            print('The daemon sent an invalid code')
            return 
        if not mute:
            print(status_messages.get(response, "The daemon sent an unknown code"))
        client_socket.close()
        return response

    def attach(self, server_name):
        subprocess.run(["tmux", "attach-session", "-t", server_name])

    def talk(self, session_name):
        pipe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../pipes/' + session_name)

        #TODO needed to copy current user input then print server message and after that paste user input
        # and fix a bug when pipe brokes
        while True:
            try:
                fd = os.open(pipe_path, os.O_RDWR)
                pipe = os.fdopen(fd, 'r')
                
                while not self.stop_event.is_set():
                    line = pipe.readline()
                    if not line:
                        raise OSError("TMUX PIPE DED :(")
                    print(line, end='')
                print('Closed')
                break
            except OSError as e:
                print(e)
                command = ['tmux', 'pipe-pane', '-o', '-t', session_name, f'cat >> {pipe_path}']
                subprocess.run(command, check=False)
                sleep(1)
    
    def send_message(self, session_name, message):
        subprocess.run(['tmux', 'send-keys', '-t', session_name, message, 'Enter'])

    def signal_handler(self, sig, frame):
        print('Signal received, stopping...')
        self.stop_event.set() 
        subprocess.run(['tmux', 'send-keys', '-t', 'red', 'enter'])
        exit()