# Minik

Minik is a CLI tool designed for managing Minecraft servers. Developed and tested on Debian/Ubuntu, it offers a range of features to streamline server control.

## Features

- **System startup integration:** Automatically starts on system boot.
- **Automatic server restart:** Restarts the Minecraft server if it crashes.
- **Safe server shutdown:** Ensures proper server shutdown when the computer is turned off.
- **Basic commands:** Start, stop, restart servers, and send messages.
- **Autocompletion:** Supports command autocompletion.

## Requirements

1. **Python:** Ensure you have Python 3.6 or higher installed. You can check your Python version with:

    ```
    python3 --version
    ```

    If needed, install Python 3.6+ using your package manager or from [Python's official website](https://www.python.org/downloads/).

    Venv and pip are also required.
    ```
    sudo apt install python3-pip -y 
    ```
    ```
    sudo apt install python3-venv -y 
    ```

2. **tmux:** Ensure `tmux` is installed. This guide assumes you are using a Debian-based system (such as Debian or Ubuntu). If `tmux` is not already installed, you can install it using:

    ```
    sudo apt install tmux -y 
    ```

   For other distributions or operating systems, please refer to your package manager's documentation for installing `tmux`.

## Installation

To install Minik, follow these steps:

1. Clone the repository:

    ```
    git clone https://github.com/Jeinerox/minik.git
    ```

2. Navigate into the cloned directory:

    ```
    cd minik
    ```

3. Make the installation scripts executable:

    ```
    sudo chmod ugo+x install.sh uninstall.sh
    ```

4. Run the installation script:

    ```
    sudo ./install.sh
    ```

5. Check if the daemon is working:

    ```
    systemctl status minikd.service
    ```

6. **Note:** After installation, you may need to open a new terminal in order for the autocomplete to work properly.

The installation script will:

- Create a virtual environment.
- Set up the systemd service for automatic startup.
- Create the executable file `minik` in `/usr/local/bin/`.
- Add eval command in .bashrc

## Configuration

After installation, you need to configure Minik. Edit the `config/servers.yaml` file. Below is an example configuration:

```
servers:
- name: server1
  path: /path/to/your/server/1
  backup_limit: 1
  backup_path: /path/to/your/backups/
  world_name: your_world_name
  memory: -Xmx3G
  auto_restart: false
  start_on_launch: false
- name: server2
  path: /path/to/your/server/2
  memory: -Xmx3G
  auto_restart: false
  start_on_launch: true
```

### Required Fields

- `name`: The name of the server. This name is used in the CLI to manage the server.
- `path`: The path to the server folder.
- `memory`: The amount of memory allocated to the server.
- `auto_restart`: Set to `true` to enable automatic server restart on crash.
- `start_on_launch`: Set to `true` to start the server automatically on system boot.

### Optional Fields

To enable backups, all three fields must be specified:

- `backup_limit`: Specifies the maximum number of backups. Backups are created daily at 5 AM local server time.
- `backup_path`: Path to the folder where backups are stored.
- `world_name`: The name of the world for the server.

## Usage

To use Minik, the general command structure is:

```
minik [option] [server_name] [args]
```

- **[option]:** The command to execute (e.g., `start`, `stop`, `restart`, etc.).
- **[server_name]:** The name of the server. Use `all` to apply the command to all configured servers.
- **[args]:** Additional arguments or flags (e.g., `-f` for force, `-w` to wait).

You can get detailed help on commands and options by running:

```
minik --help
```

### Examples

- Start `server1`:

    ```
    minik start server1
    ```

- Stop `server2` and wait for the command to complete:

    ```
    minik stop server2 -w
    ```

- Force stop `server2`:

    ```
    minik stop server2 -f
    ```

- Restart all servers:

    ```
    minik restart all
    ```

- Send a message to `server3`:

    ```
    minik say server3 "Hello!"
    ```

## Uninstallation

To uninstall Minik, from the root directory of the project, run:

```
sudo ./uninstall.sh
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit issues and pull requests. Contributions are always welcome!

## Contact

For any questions or feedback, please contact me via jeinerox@gmail.com

