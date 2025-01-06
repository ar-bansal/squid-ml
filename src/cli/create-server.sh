#!/bin/bash

usage() {
    echo "Usage: mlops create-server [help] [--rebuild]"
    echo
    echo "Build, create, and launch a complete MLflow setup on Docker. For logging, use http://localhost:5001/ as the tracking URI, or http://<ip-address>:<port>/ if using a virtual machine."
    echo
    echo "Options for 'create-server':"
    echo "  -h, --help, help      Show this help message."
    echo "  -d, --detach          Run in detached mode."
    echo "  --rebuild             Force a rebuild of the Docker image even if it exists."
    echo
    exit 1
}

check_image() {
    # Check if the 'mlflow_server' image is available on the system
    docker images --format '{{.Repository}}' | grep -q "^mlflow_server$"
    return $? 
}

get_version_info() {
    echo "Docker image 'mlflow_server' is not found or rebuild requested."
    read -p "Enter the Python version to use (e.g., 3.9): " python_version
    read -p "Enter the MLFlow version to use (e.g., 2.18.0): " mlflow_version
}

get_detached_mode() {
    while true; do
        read -p "Run in detached mode? (y/[n]): " DETACH_INPUT
        DETACH_INPUT="${DETACH_INPUT:-n}"  # Default to 'n' if input is empty

        if [[ "$DETACH_INPUT" == "y" || "$DETACH_INPUT" == "Y" ]]; then
            DETACHED_MODE=true
            break
        elif [[ "$DETACH_INPUT" == "n" || "$DETACH_INPUT" == "N" ]]; then
            DETACHED_MODE=false
            break
        else
            echo "Invalid input. Please enter 'y' for yes or 'n' for no."
        fi
    done
}

create-server() {
    REBUILD=false
    mlflow_version=""
    python_version=""
    DETACHED_MODE=false

    # Parse the command-line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --rebuild)
                REBUILD=true
                shift
                ;;
            help)
                usage
                ;;
            -d|--detach)
                DETACHED_MODE=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                usage
                ;;
        esac
    done

    if ! $DETACHED_MODE; then
        get_detached_mode
    fi

    # Check if the image exists or rebuild is requested
    if ! check_image || $REBUILD; then
        get_version_info
        echo "Building the image with Python version $python_version and MLFlow version $mlflow_version."
        BUILD_COMMAND="docker compose -f $DOCKER_COMPOSE_PATH build --build-arg python_version=$python_version --build-arg mlflow_version=$mlflow_version"
        if $DETACHED_MODE; then
            BUILD_COMMAND="$BUILD_COMMAND -d"
        fi
        echo $BUILD_COMMAND
        $BUILD_COMMAND
    fi

    UP_COMMAND="docker compose -f $DOCKER_COMPOSE_PATH up"

    if $DETACHED_MODE; then
        UP_COMMAND="$UP_COMMAND -d"
    fi

    $UP_COMMAND
}

# Main entry point
if [[ "$2" == "-h" || "$2" == "--help" || "$2" == "help" ]]; then
    usage
else
    shift
    create-server "$@"
fi
