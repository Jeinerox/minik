#!/bin/bash

REPO_PATH="$(cd "$(dirname "$0")" && pwd)"
SYSTEMD_DIR="/etc/systemd/system"
TEMPLATES_DIR="$(dirname "$0")/templates"
SERVICE_FILES_DIR="$REPO_PATH/services"

sudo systemctl stop tmux-dummy.service 
sudo systemctl stop minikd.service

sudo rm -f "$SERVICE_FILES_DIR/tmux-dummy.service"
sudo rm -f "$SERVICE_FILES_DIR/minikd.service"
sudo rm -f "$SYSTEMD_DIR/tmux-dummy.service"
sudo rm -f "$SYSTEMD_DIR/minikd.service"
sudo systemctl daemon-reload
