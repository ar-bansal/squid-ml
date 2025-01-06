import subprocess
import sys
import os


def usage():
    print("Usage: mlops <command>\n")
    print("Commands:")
    print("  help                 Show this help message.")
    print("  create-server        Build and start the Docker containers.")
    print("  destroy-server       Stop and remove Docker containers.")
    print("  start-server         Start the Docker containers.")
    print("  stop-server          Stop the running Docker containers.")
    print("  delete-data          Delete the host-mounted data folder.")
    print("\nUse 'mlops <command> help' for more details about a specific command.")
    sys.exit(1)


COMMAND_MAP = {
    "create-server": "create-server.sh",
    "destroy-server": "destroy-server.sh",
    "start-server": "start-server.sh",
    "stop-server": "stop-server.sh",
    "delete-data": "delete-data.sh"
}

def run_command(command, *args):
    # Resolve the directory of the script, even if called from anywhere
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # cli_dir = os.path.join(script_dir, "cli")

    # # Ensure that the environment variable is set
    # os.environ["DOCKER_COMPOSE_PATH"] = os.path.join(script_dir, "infra/docker-compose.yaml")
    os.environ["DOCKER_COMPOSE_PATH"] = "../infra/docker-compose.yaml"

    # Map the command to the corresponding script in the CLI directory

    if command in COMMAND_MAP.keys():
        # script_path = os.path.join(cli_dir, COMMAND_MAP[command])
        script_path = os.path.join(script_dir, COMMAND_MAP[command])
        # script_path = COMMAND_MAP[command]
        subprocess.run([script_path, command] + list(args))
    else:
        print(f"Error: Unknown command '{command}'")
        usage()

def main():
    try:
            
        if len(sys.argv) < 2:
            usage()

        command = sys.argv[1]
        args = sys.argv[2:]

        if command in COMMAND_MAP.keys():
            run_command(command, *args)
        elif command in ["help", "--help", "-h"]:
            usage()
        else:
            print(f"Error: Unknown command '{command}'")
            usage()
    except KeyboardInterrupt:
        print("\nOperation canceled.")

if __name__ == "__main__":
    main()
