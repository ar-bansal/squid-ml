#!/bin/bash

usage() {
    echo "Usage: mlops destroy-server"
    echo
    echo "Options for 'destroy-server':"
    echo "  -y                   Skip confirmation and run the destroy command."
    echo "  help                 Show this help message."
    echo
    exit 1
}

destroy-server() {
    docker compose -f $DOCKER_COMPOSE_PATH down --remove-orphans
}

# Main entry point
if [[ "$2" == "help" ]]; then
    usage
elif [[ "$2" == "-y" ]]; then
    destroy-server
elif [[ -z "$2" ]]; then
    # Ask for confirmation before running destroy-server
    read -p "Are you sure you want to destroy the server and remove the containers? (y/[n]): " confirm
    confirm="${confirm:-n}"
    if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
        destroy-server
    else
        echo "Operation canceled."
    fi
else
    echo "Error: Unknown command '$2'"
    usage
fi
