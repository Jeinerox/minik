#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run with sudo. Run sudo ./uninstall.sh" >&2
  exit 1
fi

REPO_PATH="$(cd "$(dirname "$0")" && pwd)"
SYSTEMD_DIR1="/usr/lib/systemd/system"
SYSTEMD_DIR2="/etc/systemd/system"
TEMPLATES_DIR="$(dirname "$0")/templates"
USER_HOME=$(eval echo ~"$SUDO_USER")
MINIK_PATH="/usr/local/bin/minik"

# UNINSTALLING VENV & CLI

sudo rm -R venv
sudo rm $MINIK_PATH
bashrc='eval "$(_MINIK_COMPLETE=bash_source minik)"'
sed -i "\|$bashrc|d" "$USER_HOME/.bashrc"

# UNINSTALLING SERVICES
sudo systemctl stop tmux-dummy.service 
sudo systemctl stop minikd.service
sudo rm -f "$SYSTEMD_DIR1/tmux-dummy.service"
sudo rm -f "$SYSTEMD_DIR1/minikd.service"
sudo rm -f "$SYSTEMD_DIR2/tmux-dummy.service"
sudo rm -f "$SYSTEMD_DIR2/minikd.service"
sudo systemctl daemon-reload
