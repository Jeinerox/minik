import socket
import yaml
import os
import subprocess
from time import sleep

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config/servers.yaml')
config = None

def read_yaml():
    global config
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)

def is_server_running(server):
    result = subprocess.run(['pgrep', '-f', f"{server['path']}/server.jar"], stdout=subprocess.PIPE, text=True)
    return bool(result.stdout.strip())

def start_server(server):
    result = subprocess.run(['tmux', 'list-sessions'], stdout=subprocess.PIPE, text=True)
    if server['name'] not in result.stdout:
        subprocess.run(['tmux', 'new-session', '-d', '-s', server['name']])
    if (is_server_running(server)):
        return
    command = f"cd {server['path']} ; /usr/bin/java {server['memory']} -jar {server['path']}/server.jar nogui"
    subprocess.run(['tmux', 'send-keys', '-t', server['name'], command, 'enter'])

def stop_server(server, wait=False):
    if (is_server_running(server)):
       subprocess.run(['tmux', 'send-keys', '-t', server['name'], 'stop', 'enter']) 
    if wait:
        while is_server_running(server):
            sleep(0.5)

def stop_force_server(server):
    if (is_server_running(server)):
       subprocess.run(['tmux', 'kill-session', '-t', server['name']]) 

def restart_server(server):
    if (is_server_running(server)):
        stop_server(server, wait=True)
        start_server(server)

def servers_run_checker():
    while True:
        sleep(5)

def command_handler(command, client_socket):
    try:
        server_name, command = command.split()
        server = next((s for s in config['servers'] if s['name'] == server_name), None)
        if server:
            if command == 'start':
                start_server(server)
            elif command == 'stop':
                stop_server(server)
            elif command == 'force-stop':
                stop_force_server(server)
            elif command == 'status':
                if is_server_running(server):
                    client_socket.sendall(f"Server {server['name']} is running.\n".encode('utf-8'))
                else:
                    client_socket.sendall(f"Server {server['name']} is not running.\n".encode('utf-8'))
            elif command == 'list':
                subprocess.run(['tmux', 'send-keys', '-t', server['name'], 'list', 'C-m'])
                client_socket.sendall(b"List command sent.\n")
            client_socket.sendall(b'Command executed\n')
        else:
            client_socket.sendall(b'Server not found\n')
    finally:
        client_socket.close()

def api():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 9198))
    server_socket.listen(1)

    while True:
        client_socket, addr = server_socket.accept()
        with client_socket:
            print('Connected by', addr)
            data = client_socket.recv(1024)
            if not data:
                break
            command = data.decode('utf-8')
            print(f"Received command: {command}")
            command_handler(command, client_socket)

def main():
    read_yaml()
    for server in config['servers']:
        if server['start_on_launch']:
            start_server(server)
    api()

if __name__ == "__main__":
    main()