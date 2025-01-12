import os
from python_on_whales import DockerClient


# def _create_docker_client():
#     # Lazy import 

#     server_dir = os.path.dirname(os.path.abspath(__file__))
#     infra_dir = os.path.join(server_dir, "infra")
#     COMPOSE_FILE = os.path.join(infra_dir, "docker-compose.yaml")
#     COMPOSE_ENV_FILE = os.path.join(infra_dir, ".env")
#     docker = DockerClient(compose_files=[COMPOSE_FILE], compose_env_files=[COMPOSE_ENV_FILE])

#     return docker


def _set_mlops_data_dir(): # Set the volume mounting directory as <user PWD>/mlops_data
    MLOPS_DATA_DIR = os.path.join(os.getcwd(), "mlops_data")
    os.makedirs(MLOPS_DATA_DIR, exist_ok=True)
    os.environ["MLOPS_VOLUME_MOUNT_DIR"] = MLOPS_DATA_DIR


def _set_ports(ui_port: int, artifact_store_port: int, console_port: int, backend_port: int):
    os.environ["UI_PORT"] = str(ui_port)
    os.environ["MINIO_OBJ_STORE_PORT"] = str(artifact_store_port)
    os.environ["MINIO_CONSOLE_PORT"] = str(console_port)
    os.environ["POSTGRES_PORT"] = str(backend_port)
  

def _delete_all_data(path) -> None:
    """
    Delete a directory and all its contents. 
    """
    # Lazy import 
    import shutil

    if os.path.exists(path):
        try:
            os.chmod(path, 0o777)
            shutil.rmtree(path)
        except Exception as e:
            print("Could not delete the mounted volumes due to the following error. Please delete them manually.")
            print(e)


class Server:
    def __init__(self, ui_port: int=5000, artifact_store_port: int=9000, console_port: int=9001, backend_store_port: int=5432,):
        self.ui_port = ui_port
        self.artifact_store_port = artifact_store_port
        self.console_port = console_port
        self.backend_store_port = backend_store_port

        server_dir = os.path.dirname(os.path.abspath(__file__))
        infra_dir = os.path.join(server_dir, "infra")
        COMPOSE_FILE = os.path.join(infra_dir, "docker-compose.yaml")
        COMPOSE_ENV_FILE = os.path.join(infra_dir, ".env")
        docker = DockerClient(compose_files=[COMPOSE_FILE], compose_env_files=[COMPOSE_ENV_FILE])
        self.docker = docker


    def start(self, quiet: bool=True,  python_version: str=None, mlflow_version: str=None) -> None:
        """
        Create and start the tracking server, backend store, and artifact store containers. 

        If python_version and mlflow_version are provided, a new version of the mlflow image
        is built using the Python and MLflow version. 
        """
        # docker = _create_docker_client()
        _set_mlops_data_dir()   # Used here for host mounting the volumes
        _set_ports(
            self.ui_port, 
            self.artifact_store_port, 
            self.console_port, 
            self.backend_store_port
            )

        # Rebuild if both python_version and mlflow_version are passed. 
        if python_version and mlflow_version:
            self.docker.compose.build(build_args={
                "python_version": python_version, 
                "mlflow_version": mlflow_version
            }, 
            quiet=quiet)

        elif python_version or mlflow_version:
            # Skip rebuild
            argument = "python_version" if python_version else "mlflow_version"
            print(f"Skipping rebuild as {argument} was not provided. Provide both python_version and mlflow_version to rebuild the mlflow image.")
        
        # Start containers
        self.docker.compose.up(detach=True, pull="missing", quiet=quiet)


    def stop(self) -> None:
        """
        Stop the running containers. 
        """
        # docker = _create_docker_client()
        self.docker.compose.stop()


    def destroy(self, delete_all_data=False) -> None:
        """
        Stop and delete all the associated containers. 

        If delete_all_data is True, then the host-mounted volumes will be removed. ALL DATA WILL BE LOST. 
        """
        _set_mlops_data_dir()
        self.docker.compose.down(remove_orphans=True)

        if delete_all_data:
            _delete_all_data(os.environ["MLOPS_VOLUME_MOUNT_DIR"])




# def main():
#     # Lazy import 
#     import argparse

#     parser = argparse.ArgumentParser(description="Manage MLOps infrastructure with start, stop, and destroy commands.")
#     subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

#     # `start` command
#     start_parser = subparsers.add_parser("start", help="Start the MLOps infrastructure")
#     start_parser.add_argument("--quiet", action="store_true", help="Run Docker commands in quiet mode")
#     start_parser.add_argument("--python-version", type=str, help="Specify the Python version for rebuilding the image")
#     start_parser.add_argument("--mlflow-version", type=str, help="Specify the MLflow version for rebuilding the image")

#     # `stop` command
#     subparsers.add_parser("stop", help="Stop the MLOps infrastructure")

#     # `destroy` command
#     destroy_parser = subparsers.add_parser("destroy", help="Destroy the MLOps infrastructure")
#     destroy_parser.add_argument("--delete-all-data", action="store_true", help="Delete all mounted volumes (ALL DATA WILL BE LOST)")

#     # Parse arguments
#     args = parser.parse_args()

#     # Dispatch to the appropriate function
#     if args.command == "start":
#         start(quiet=args.quiet, python_version=args.python_version, mlflow_version=args.mlflow_version)
#     elif args.command == "stop":
#         stop()
#     elif args.command == "destroy":
#         destroy(delete_all_data=args.delete_all_data)


# if __name__ == "__main__":
#     main()