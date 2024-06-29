import socket
import subprocess

class ServerManager:
    def __init__(self, config_file='../config/servers.yaml'):
        self.config_file = config_file

    def send_command(self, command, server_name):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 9198))
        client_socket.sendall(f"{server_name} {command}".encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(response)
        client_socket.close()

    def attach(self, server_name):
        subprocess.run(["tmux", "attach-session", "-t", server_name])
