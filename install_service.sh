#!/bin/bash

sudo ./uninstall_service.sh

TEMPLATES_DIR="$(dirname "$0")/templates"
REPO_PATH="$(cd "$(dirname "$0")" && pwd)"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_FILES_DIR="$REPO_PATH/services"
USERNAME=${SUDO_USER:-$(whoami)}

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

sudo ln -sf "$SERVICE_FILES_DIR/tmux-dummy.service" "$SYSTEMD_DIR/tmux-dummy.service"
sudo ln -sf "$SERVICE_FILES_DIR/minikd.service" "$SYSTEMD_DIR/minikd.service"

sudo systemctl daemon-reload
sudo systemctl enable tmux-dummy.service
sudo systemctl enable minikd.service

sudo systemctl start tmux-dummy.service
sudo systemctl start minikd.service
