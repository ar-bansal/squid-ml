#!/bin/bash

usage() {
    echo "Usage: mlops start-server"
    echo
    echo "Start the server if already created. If not, run 'mlops create-server' to create a server."
    echo
    echo "Options for 'start-server':"
    echo "  This command does not accept any options."
    echo
    exit 1
}

start-server() {
    docker compose -f $DOCKER_COMPOSE_PATH start 2>/dev/null
    if [[ $? -ne 0 ]]; then
        usage
    fi
}

if [[ "$2" == "help" ]]; then
    usage
elif [[ -z "$2" ]]; then
    shift
    start-server "$@"
else
    echo "Error: Unknown command '$2'"
    usage
fi