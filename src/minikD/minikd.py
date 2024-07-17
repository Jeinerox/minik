import socket
import yaml
import os
import subprocess
import threading
import logging
import signal
from logger import my_logger
from backup import Backup
from yamltester import YamlTester
from time import sleep

PORT = 9198
BACKUP_TIME = 5 # hours
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config/servers.yaml')
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs/minik.log')
PIPES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../pipes/')

config = None
minikd_logger = my_logger(LOG_PATH, 'MinikD', logging.DEBUG)
backup = Backup(minikd_logger, BACKUP_TIME)
yaml_tester = YamlTester(CONFIG_PATH, minikd_logger)


def read_yaml():
    global config
    config = yaml_tester.safe_read_yaml()

def save_yaml():
    global config
    with open(CONFIG_PATH, 'w') as file:
        yaml.safe_dump(config, file, default_flow_style=False, sort_keys=False)
    minikd_logger.debug(f"[YAML] Config saved.")

def is_server_running(server):
    result = subprocess.run(['pgrep', '-f', f"{server['path']}/server.jar"], stdout=subprocess.PIPE, text=True)
    return bool(result.stdout.strip())

def start_server(server):
    minikd_logger.info(f"[{server['name']}] Trying to start the server.")
    server['auto_restart'] = True
    save_yaml()
    result = subprocess.run(['tmux', 'list-sessions'], stdout=subprocess.PIPE, text=True)

    if server['name'] not in result.stdout:
        minikd_logger.debug(f"[{server['name']}] Starting new tmux session.")
        subprocess.run(['tmux', 'new-session', '-d', '-s', server['name']])
        pipe_path = f"{PIPES_PATH}/{server['name']}"
        if not os.path.exists(pipe_path):
            os.mkfifo(pipe_path)
        subprocess.run(['tmux', 'pipe-pane', '-o', '-t', server['name'], f'cat >> {pipe_path}'])
        sleep(0.5)

    if (is_server_running(server)):
        minikd_logger.debug(f"[{server['name']}] There was an attempt to start the server, but it is already running.")
        return 101
    
    command = f"cd {server['path']} ; /usr/bin/java {server['memory']} -jar {server['path']}/server.jar nogui"
    send_text(server, command)

    for i in range(5): # i don't like this too
        if (is_server_running(server)):
            minikd_logger.info(f"[{server['name']}] The server has been started.")
            return 201
        sleep(0.5)
    minikd_logger.info(f"[{server['name']}] An error occurred when starting the server.")
    return 501

def stop_server(server, wait=False):
    minikd_logger.info(f"[{server['name']}] Trying to stop the server.")
    server['auto_restart'] = False
    save_yaml()
    if (is_server_running(server)):
        send_text(server, 'stop', reliable=True)
    else:
        minikd_logger.debug(f"[{server['name']}] There was an attempt to stop the server, but it is already stopped.")
        return 102
    if wait:
        while is_server_running(server):
            sleep(0.5)
        minikd_logger.info(f"[{server['name']}] The server has been stopped.")
        return 202
    minikd_logger.info(f"[{server['name']}] A stop command has been sent.")
    return 100
    
def stop_force_server(server, wait=False):
    server['auto_restart'] = False
    save_yaml()
    subprocess.run(['tmux', 'kill-session', '-t', server['name']])
    minikd_logger.debug(f"[{server['name']}] Tmux session closed.")
    sleep(0.5)
    if wait:
        while is_server_running(server):
            sleep(0.5)
        minikd_logger.info(f"[{server['name']}] The server has been stopped by force.")
        return 202
    return 100

def restart_server(server, wait=False, force=False):
    if force:
        stop_force_server(server, wait)
    else:
        stop_server(server, wait)

    start_server(server)
    minikd_logger.info(f"[{server['name']}] The server has been restarted.")
    return 201

def backup_servers(manual = False):
    backedUp = False
    for server in config['servers']:
        if 'backup_path' not in server or 'world_name' not in server:
            continue
        minikd_logger.info(f"[{server['name']}] The backup begins.")
        if is_server_running(server) and not manual:
            send_text(server, 'say The server will reboot in 20 seconds for backup.')
            sleep(20)
            stop_server(server, wait=True)
        elif is_server_running(server):
            stop_server(server, wait=True)
        backup.backup(server['path'], server['backup_path'], server['world_name'], server.get('backup_limit', 10))
        start_server(server)
        minikd_logger.info(f"[{server['name']}] The backup was successfully created.")
        backedUp = True

    if backedUp:
        return 203
    return 302

def change_start_on_lauch(server, state):
    server['start_on_launch'] = state
    save_yaml()
    if state:
        minikd_logger.info(f"[{server['name']}] Start on lauch turned on.")
        return 204
    minikd_logger.info(f"[{server['name']}] Start on lauch turned off.")
    return 205

def send_text(server, message, reliable=False):
    if reliable:
        subprocess.run(['tmux', 'send-keys', '-t', server['name'], 'Enter'])
    subprocess.run(['tmux', 'send-keys', '-t', server['name'], message, 'Enter'])
    minikd_logger.debug(f"[{server['name']}] The message has been sent: {message}")

def watchdog():
    while True:
        read_yaml()
        if not config:
            minikd_logger.error(f"Daemon is suspended due to invalid config, waiting...")
            while not config:
                read_yaml()
                sleep(1)
            minikd_logger.info(f"The daemon is resumed.")

        for server in config['servers']:
            if server['auto_restart'] == True and not is_server_running(server):
                minikd_logger.warning(f"[{server['name']}] Restarting the server after a probable crash.")
                start_server(server)

        if backup.is_ready():
            backup_servers()

        sleep(5)
  
def command_handler(command, client_socket):
    answer = b'401'
    try:
        read_yaml()
        if not config:
            answer = b'300'
            raise RuntimeError('Bad config')
        
        command, server_name = command.split()
        server = next((s for s in config['servers'] if s['name'] == server_name or '-' == server_name ), None)
        if server:
            if command == 'test':
                answer = b'200'
            elif command == 'start':
                answer = str(start_server(server)).encode('utf-8')
            elif command == 'stop':
                answer = str(stop_server(server)).encode('utf-8')    
            elif command == 'backup':
                answer = b'100' 
                threading.Thread(target=backup_servers, args=(True,)).start()
            elif command == 'backup-w':
                answer = str(backup_servers(True)).encode('utf-8')
            elif command == 'stop-w':
                answer = str(stop_server(server, wait=True)).encode('utf-8')
            elif command == 'stop-f':
                answer = str(stop_force_server(server)).encode('utf-8')
            elif command == 'stop-f-w':
                answer = str(stop_force_server(server, wait=True)).encode('utf-8')
            elif command == 'restart':
                answer = str(restart_server(server)).encode('utf-8')
            elif command == 'restart-w':
                answer = str(restart_server(server, wait=True)).encode('utf-8')
            elif command == 'restart-f':
                answer = str(restart_server(server, force=True)).encode('utf-8')
            elif command == 'restart-f-w':
                answer = str(restart_server(server, wait=True, force=True)).encode('utf-8')
            elif command == 'enable':
                answer = str(change_start_on_lauch(server, True)).encode('utf-8')
            elif command == 'disable':
                answer = str(change_start_on_lauch(server, False)).encode('utf-8')
            elif command == 'status':
                answer =  [b'102', b'101'][int(is_server_running(server))]
            else:
                answer = b'401'
        else:
            answer = b'301'
    except BaseException as e:
        minikd_logger.error(f"[API] An error occurred while processing the request: {e}.")
    finally:
        client_socket.sendall(answer)
        minikd_logger.debug(f"[API] Sent code: {answer}")
        client_socket.close()
    
def api():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', PORT))
    server_socket.listen(1)
    minikd_logger.debug(f"[API] Server listening on port: {PORT}.")
    while True:
        client_socket, addr = server_socket.accept()
        minikd_logger.debug(f"[API] Connected by: {addr}.")
        with client_socket:
            data = client_socket.recv(1024)
            if not data:
                break
            command = data.decode('utf-8')
            minikd_logger.debug(f"[API] Received command: {command}.")
            command_handler(command, client_socket)

def signal_handler(sig, frame):
    minikd_logger.info(f"[SIG] Received CTRL+C, stopping...")

    if config:
        server_threads = []
        for server in config['servers']:
            if is_server_running(server):
                server_threads.append(threading.Thread(target=stop_server, args=(server, True,))) #simultaneous stop
                server_threads[-1].start()

        for server in server_threads:
            server.join()
    
    minikd_logger.info(f"Daemon stopped.") 
    os._exit(0) # kills blocking .accept() from api()

def main():
    minikd_logger.info('Starting daemon...')
    signal.signal(signal.SIGINT, signal_handler)
    apiThread = threading.Thread(target=api)
    apiThread.start()
    read_yaml()
    while not config:
        read_yaml()
        sleep(1)

    for server in config['servers']:
        if server['start_on_launch']:
            start_server(server)
        else:
            server['auto_restart'] = False
            save_yaml()
    minikd_logger.info('Daemon started successfully.')
    watchdog()

if __name__ == "__main__":
    main()