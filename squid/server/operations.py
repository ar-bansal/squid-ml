import os
import sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
from python_on_whales import DockerClient
import mlflow
import re


class Server:
    """
    A helper class to manage an MLflow tracking server using Docker Compose.

    The Server class simplifies starting, stopping, and managing an MLflow 
    tracking server. It handles environment configuration (ports, project name, 
    Python/MLflow versions), ensures Docker images are built when necessary, 
    and provides lifecycle management for the containers.

    Attributes:
        project_name (str): The name of the ML project (used as the Docker Compose project name).
        ui_port (int): Port number for the MLflow UI.
        artifact_store_port (int): Port number for the artifact store.
        console_port (int): Port number for the console.
    """
    def __init__(self, project_name=None, ui_port=5001, artifact_store_port=5002, console_port=5003) -> None:
        """
        Initialize the Server instance.

        Args:
            project_name (str, optional): Name of the project. Defaults to current working directory name if not provided.
            ui_port (int, optional): Port for the MLflow UI. Defaults to 5001.
            artifact_store_port (int, optional): Port for the artifact store. Defaults to 5002.
            console_port (int, optional): Port for the console. Defaults to 5003.
        """

        if not project_name:
            project_name = os.path.basename(os.getcwd())

        self.project_name = project_name
        self.ui_port = ui_port
        self.artifact_store_port = artifact_store_port
        self.console_port = console_port

        mlflow.set_tracking_uri(f"http://localhost:{self.ui_port}")

        self._set_project_name()
        self._set_ports()

        self._python = ""
        self._mlflow = ""

        self.docker = self._create_docker_client()

    def _create_docker_client(self) -> DockerClient:
        """
        Create a Docker client configured with the project's docker-compose file.

        Returns:
            DockerClient: A Docker client instance configured for the project.
        """

        server_dir = Path(__file__).resolve().parent
        docker_compose_file = server_dir / "infra" / "docker-compose.yaml"
        docker = DockerClient(
            compose_files=[docker_compose_file], 
            compose_project_name=self.project_name
            )

        return docker

    def _set_ports(self):
        """Set environment variables for the ports used by the MLflow UI, artifact store, and console."""
        os.environ["SQUID_ML_UI_PORT"] = str(self.ui_port)
        os.environ["SQUID_ML_ARTIFACT_STORE_PORT"] = str(self.artifact_store_port)
        os.environ["SQUID_ML_CONSOLE_PORT"] = str(self.console_port)

    def _set_versions(self, python_: str, mlflow_: str):
        """
        Validate and set Python and MLflow versions as environment variables.

        Args:
            python_ (str): Python version in the format '<major>.<minor>', e.g., '3.10'. Empty string allowed.
            mlflow_ (str): MLflow version in the format '<major>.<minor>.<patch>', e.g., '2.18.0'. Empty string allowed.

        Raises:
            ValueError: If the provided versions do not match the expected format.
        """
        if python_ and not bool(re.match(r"^\d+\.\d+$", python_)):
            raise ValueError(f"Python version must be of the form '<major>.<minor>', like '3.10'. Provided '{python_}'")
        if mlflow_ and not bool(re.match(r"^\d+\.\d+\.\d+$", mlflow_)):
            raise ValueError(f"MLflow version must be of the form '<major>.<minor>.<patch>', like '2.18.0'. Provided '{mlflow_}'")

        os.environ["SQUID_ML_PYTHON_VERSION"] = python_
        self._python = python_
        os.environ["SQUID_ML_MLFLOW_VERSION"] = mlflow_
        self._mlflow = mlflow_
    
    def _set_project_name(self):
        """Set the project name as an environment variable."""
        os.environ["SQUID_ML_PROJECT_NAME"] = self.project_name


    def start(self, quiet=True, use_current_env=False, python_version="", mlflow_version=""):
        """
        Start the MLflow server using Docker Compose.

        Args:
            quiet (bool, optional): Whether to suppress Docker build and compose output. Defaults to True.
            use_current_env (bool, optional): If True, use the current environment's Python and MLflow versions. Defaults to False.
            python_version (str, optional): Python version in the format '<major>.<minor>'. Required if not using current env. Defaults to "".
            mlflow_version (str, optional): MLflow version in the format '<major>.<minor>.<patch>'. Required if not using current env. Defaults to "".

        Raises:
            ModuleNotFoundError: If use_current_env=True but MLflow is not installed.
            ValueError: If required versions are missing or in the wrong format.
        """
        if use_current_env: 
            try:
                mlflow_version = version("mlflow")
            except PackageNotFoundError:
                message = "MLflow is not installed in the current environment. Either install it, or specify mlflow_version <major.minor.patch>."
                raise ModuleNotFoundError(message)
            
            v_info = sys.version_info
            python_version = f"{v_info.major}.{v_info.minor}"

        self._set_versions(python_=python_version, mlflow_=mlflow_version)

        if not self.docker.image.exists("mlflow_server") and not (python_version and mlflow_version) and not use_current_env:
            message = "Docker image mlflow_server not found. Please use use_current_enviroment=True or specify python_version <major.minor> and mlflow_version <major.minor.patch> to proceed."
            raise ValueError(message)
        elif use_current_env or (python_version and mlflow_version):
            self.docker.compose.build(quiet=quiet)
        elif not use_current_env and (python_version or mlflow_version):
            argument = "python_version" if python_version else "mlflow_version"
            message = f"Both python_version and mlflow_version must be provided for building the image. Only {argument} was provided."
            raise ValueError(message)

        # TODO: Change to docker compose start if the project already exists. 
        self.docker.compose.up(detach=True, quiet=quiet)

    def stop(self):
        """Stop the running MLflow server containers without removing them."""
        self.docker.compose.stop()

    def down(self, quiet=True, delete_all_data=False):
        """
        Stop and remove the MLflow server containers and associated resources.

        Args:
            quiet (bool, optional): Whether to suppress Docker compose output. Defaults to True.
            delete_all_data (bool, optional): If True, delete associated volumes (all stored data). Defaults to False.
        """
        self._set_versions(python_=self._python, mlflow_=self._mlflow)

        self.docker.compose.down(
            remove_orphans=True, 
            volumes=delete_all_data, 
            quiet=quiet
            )
