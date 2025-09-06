import os
import sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
from python_on_whales import DockerClient
import mlflow
import re


class Server:
    def __init__(self, project_name=None, ui_port=5001, artifact_store_port=5002, console_port=5003):
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

    def _create_docker_client(self):
        server_dir = Path(__file__).resolve().parent
        docker_compose_file = server_dir / "infra" / "docker-compose.yaml"
        docker = DockerClient(
            compose_files=[docker_compose_file], 
            compose_project_name=self.project_name
            )

        return docker

    def _set_ports(self):
        os.environ["SQUID_ML_UI_PORT"] = str(self.ui_port)
        os.environ["SQUID_ML_ARTIFACT_STORE_PORT"] = str(self.artifact_store_port)
        os.environ["SQUID_ML_CONSOLE_PORT"] = str(self.console_port)

    def _set_versions(self, python_: str, mlflow_: str):
        # Validate version format for Python and MLflow. Empty strings are valid. 
        if python_ and not bool(re.match(r"^\d+\.\d+$", python_)):
            raise ValueError(f"Python version must be of the form '<major>.<minor>', like '3.10'. Provided '{python_}'")
        if mlflow_ and not bool(re.match(r"^\d+\.\d+\.\d+$", mlflow_)):
            raise ValueError(f"MLflow version must be of the form '<major>.<minor>.<patch>', like '2.18.0'. Provided '{mlflow_}'")

        os.environ["SQUID_ML_PYTHON_VERSION"] = python_
        self._python = python_
        os.environ["SQUID_ML_MLFLOW_VERSION"] = mlflow_
        self._mlflow = mlflow_
    
    def _set_project_name(self):
        os.environ["SQUID_ML_PROJECT_NAME"] = self.project_name


    def start(self, quiet=True, use_current_env=False, python_version="", mlflow_version=""):
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
        self.docker.compose.stop()

    def down(self, quiet=True, delete_all_data=False):
        self._set_versions(python_=self._python, mlflow_=self._mlflow)

        self.docker.compose.down(
            remove_orphans=True, 
            volumes=delete_all_data, 
            quiet=quiet
            )
