import click
from apiclient import ApiClient
import yaml
import os
# import threading
# import signal

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config/servers.yaml')
client = ApiClient()

def check():
	answer = client.send_command('test', '-', mute=True)
	if answer == 200:
		return
	elif answer == 300:
		print('YAML error. Please, check daemon logs by running: systemctl status minikd.service')
	exit(answer)

def get_servers():
	with open(CONFIG_PATH, 'r') as file:
		config = yaml.safe_load(file)
	return [server['name'] for server in config['servers'] if server['name'] is not None]


def is_all(server):
	if server == 'all':
		return get_servers()
	return [server]

@click.group()
def cli():
    pass

@cli.command()
@click.option('-w', '--wait', is_flag=True, default=False, help="Wait for the servers to backup.")
def backup(wait):
	'''Makes a backup of all servers with backup enabled. To enable it, you need to fill these fields in the config\n
		backup_count backup_path world_name'''
	if wait:
		client.send_command('backup-w', '-')
	else:
		client.send_command('backup', '-')
	
@cli.command()
@click.argument('server_name', type=click.Choice(get_servers() + ['all'], case_sensitive=False))
def start(server_name):
	'''Starts the server(s)'''
	for server_name in is_all(server_name):
		print(server_name, end=': ')
		client.send_command('start', server_name)

@cli.command()
@click.argument('server_name', type=click.Choice(get_servers() + ['all'], case_sensitive=False))
@click.option('-w', '--wait', is_flag=True, default=False, help="Wait for the server to stop.")
@click.option('-f', '--force', is_flag=True, default=False, help="Force stop the server.")
def stop(server_name, wait, force):
	'''Stops the server(s)'''
	for server_name in is_all(server_name):
		print(server_name, end=': ')
		if not wait and not force:
			client.send_command('stop', server_name) # idiot-style-f-w   :)
		elif wait and not force:
			client.send_command('stop-w', server_name)
		elif not wait and force:
			client.send_command('stop-f', server_name)
		else:
			client.send_command('stop-f-w', server_name)

@cli.command()
@click.argument('server_name', type=click.Choice(get_servers() + ['all'], case_sensitive=False))
@click.option('-w', '--wait', is_flag=True, default=False, help="Wait for the server to restart.")
@click.option('-f', '--force', is_flag=True, default=False, help="Force stop the server.")
def restart(server_name, wait, force):
	'''Restart the server(s)'''
	for server_name in is_all(server_name):
		print(server_name, end=': ')
		if not wait and not force:
			client.send_command('restart', server_name) # idiot-style-f-w   :)
		elif wait and not force:
			client.send_command('restart-w', server_name)
		elif not wait and force:
			client.send_command('restart-f', server_name)
		else:
			client.send_command('restart-f-w', server_name)

@cli.command()
@click.argument('server_name', type=click.Choice(get_servers() + ['all'], case_sensitive=False))
def enable(server_name):
	'''Enables start on launch'''
	for server_name in is_all(server_name):
		print(server_name, end=': ')
		client.send_command('enable', server_name)

@cli.command()
@click.argument('server_name', type=click.Choice(get_servers() + ['all'], case_sensitive=False))
def disable(server_name):
	'''Disables start on launch'''
	for server_name in is_all(server_name):
		print(server_name, end=': ')
		client.send_command('disable', server_name)

@cli.command()
@click.argument('server_name', type=click.Choice(get_servers() + ['all'], case_sensitive=False))
def status(server_name):
	'''Returns the server(s) status'''
	for server_name in is_all(server_name):
		print(server_name, end=': ')
		client.send_command('status', server_name)
    
@cli.command()
@click.argument('server_name', type=click.Choice(get_servers(), case_sensitive=False))
def attach(server_name):
	'''Attach to the tmux console of the selected server. To exit the console, press CTRL+B and then D.'''
	client.attach(server_name)

'''                                ====== BROKEN ======
@cli.command()
@click.argument('server_name', type=click.Choice(get_servers(), case_sensitive=False))
def talk(server_name):
	,,,An analogue of the attach command. The difference is that talk allows you to read and print 
	to the tmux console without directly connecting to it. It may work unstable, so attach is preferable.,,,
	if client.send_command('status', server_name, mute=True) == 101:
		signal.signal(signal.SIGINT, client.signal_handler)
		talkThread = threading.Thread(target=client.talk, args=(server_name,))
		talkThread.start()
		while not client.stop_event.is_set():
			message = input()
			client.send_message(server_name, message) 
	else:
		print('The server is stoppped')
'''
@cli.command()
@click.argument('server_name', type=click.Choice(get_servers() + ['all'], case_sensitive=False))
@click.argument('text', type=click.STRING)
def say(server_name, text):
	'''Sends your text message to the server. Uses the minecraft say command'''
	for server_name in is_all(server_name):
		print(server_name, end=': ')
		if client.send_command('status', server_name, mute=True) == 101:
			client.send_message(session_name=server_name, message= ('say ' + text))
			print('Sent')
		else:
			print('The server is stoppped')

@cli.command()
@click.argument('server_name', type=click.Choice(get_servers(), case_sensitive=False))
@click.argument('text', type=click.STRING)
def command(server_name, text):
	'''Sends your command to the server. Like gamemode or time set.'''
	if client.send_command('status', server_name, mute=True) == 101:
		client.send_message(session_name=server_name, message=text)
	else:
		print('The server is stoppped')
	
if __name__ == "__main__":
	check()
	cli()
