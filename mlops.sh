#!/bin/bash

usage() {
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  create-server        Build and start the Docker containers."
    echo "  destroy-server       Stop and remove Docker containers."
    echo "  start-server         Start the Docker containers."
    echo "  stop-server          Stop the running Docker containers."
    echo "  help                 Show this help message."
    echo
    echo "Use '$0 <command> --help' for more details about a specific command."
    exit 1
}


export DOCKER_COMPOSE_PATH="infra/docker-compose.yaml"

# Dispatch to specific command scripts based on user input
case "$1" in
    "create-server")
        shift
        ./cli/create-server.sh create-server "$@"
        ;;
    "destroy-server")
        shift
        ./cli/destroy-server.sh destroy-server "$@"
        ;;
    "start-server")
        shift
        ./cli/start-server.sh start-server "$@"
        ;;
    "stop-server")
        shift
        ./cli/stop-server.sh stop-server "$@"
        ;;
    "help" | "--help")
        usage
        ;;
    *)
        echo "Error: Unknown command '$1'"
        usage
        ;;
esac
