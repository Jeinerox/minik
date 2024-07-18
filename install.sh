#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run with sudo. Run sudo ./install.sh" >&2
  exit 1
fi

TEMPLATES_DIR="$(dirname "$0")/templates"
REPO_PATH="$(cd "$(dirname "$0")" && pwd)"
SYSTEMD_DIR="/usr/lib/systemd/system"
SERVICE_FILES_DIR="$REPO_PATH/services"
USERNAME=${SUDO_USER:-$(whoami)}
USER_HOME=$(eval echo ~"$SUDO_USER")
MINIK_PATH="/usr/local/bin/minik"


# INSTALLING VENV & CLI

if [ ! -f "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "#!$REPO_PATH/venv/bin/python" > "$MINIK_PATH"  # Modern problems require modern solutions :)
echo "from cli import cli" >> "$MINIK_PATH"          # I just want my script to be in the src folder
echo "if __name__ == '__main__':" >> "$MINIK_PATH"   # and not somewhere in .local like pipx does.
echo "    cli()" >> "$MINIK_PATH"                    # That's why I don't use the installer.
chmod +x "$MINIK_PATH"

echo "$REPO_PATH/src/cli" > $(python -c "import site; print(site.getsitepackages()[0])")/cli.pth

bashrc='eval "$(_MINIK_COMPLETE=bash_source minik)"'
if ! grep -qF "$bashrc" "$USER_HOME/.bashrc"; then
  echo "$bashrc" >> "$USER_HOME/.bashrc"
  echo "Autocomlete command added to .bashrc"
fi


# INSTALLING SERVICES
generate_service_file() {
    local template_file="$1"
    local repo_path="$2"
    local username="$3"
    local output_file="$4"
    
    sed -e "s|@repo_path@|${repo_path}|g" -e "s|@name@|${username}|g" "$template_file" > "$output_file"
}


mkdir -p "$SERVICE_FILES_DIR"
generate_service_file "$TEMPLATES_DIR/tmux-dummy.service.template" "$REPO_PATH" "$USERNAME" "$SERVICE_FILES_DIR/tmux-dummy.service"
generate_service_file "$TEMPLATES_DIR/minikd.service.template" "$REPO_PATH" "$USERNAME" "$SERVICE_FILES_DIR/minikd.service"

ln -sf "$SERVICE_FILES_DIR/tmux-dummy.service" "$SYSTEMD_DIR/tmux-dummy.service"
ln -sf "$SERVICE_FILES_DIR/minikd.service" "$SYSTEMD_DIR/minikd.service"

systemctl daemon-reload
systemctl enable tmux-dummy.service
systemctl enable minikd.service

systemctl start tmux-dummy.service
systemctl start minikd.service

