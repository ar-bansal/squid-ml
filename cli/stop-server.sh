#!/bin/bash

usage() {
    echo "Usage: mlops start-server"
    echo
    echo "Stop the server if running."
    echo
    echo "Options for 'start-server':"
    echo "  This command does not accept any options."
    echo
    exit 1
}

stop-server() {
    docker compose -f $DOCKER_COMPOSE_PATH stop 2>/dev/null
    if [[ $? -ne 0 ]]; then
        usage
    fi
}

if [[ "$2" == "help" ]]; then
    usage
elif [[ -z "$2" ]]; then
    shift
    stop-server "$@"
else
    echo "Error: Unknown command '$2'"
    usage
fi