import click
from server_manager import ServerManager

daemon_commands = ['start', 'stop', 'stop-force', 'list', 'status']
client_commands = ['attach']

@click.command()
@click.argument('command', type=click.Choice(daemon_commands + client_commands, case_sensitive=False))
@click.argument('server_name')
def cli(server_name, command):
    """Send a command to the server or attach to a tmux session."""
    manager = ServerManager()
    
    if command in daemon_commands:
        manager.send_command(command, server_name)
    elif command == 'attach':
        manager.send_command('status', server_name)
        manager.attach(server_name)

if __name__ == "__main__":
    cli()
