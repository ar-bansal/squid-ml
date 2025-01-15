import os
from python_on_whales import DockerClient
import mlflow
import re


def create_client():
    # TODO: Change compose file path to relative path. It should be 
    # dynamically fetched from the package.
    docker = DockerClient(
        compose_files=["infra/docker-compose.yaml"]
    )

    return docker


def _set_project_dir(project_dir):
    os.environ["PROJECT_DIR"] = project_dir


def _set_ports(ui_port, artifact_store_port, console_port):
    os.environ["UI_PORT"] = str(ui_port)
    os.environ["ARTIFACT_STORE_PORT"] = str(artifact_store_port)
    os.environ["CONSOLE_PORT"] = str(console_port)


def _set_versions(python_: str="", mlflow_: str=""):
    # Validate version format for Python and MLflow
    if python_ and not bool(re.match(r"^\d+\.\d+$", python_)):
        raise ValueError(f"Python version must be of the form '<major>.<minor>', like '3.10'. Provided '{python_}'")
    if mlflow_ and not bool(re.match(r"^\d+\.\d+\.\d+$", mlflow_)):
        raise ValueError(f"MLflow version must be of the form '<major>.<minor>.<patch>', like '2.18.0'. Provided '{mlflow_}'")

    os.environ["PYTHON_VERSION"] = python_
    os.environ["MLFLOW_VERSION"] = mlflow_


class Server:
    def __init__(self, ui_port=5001, artifact_store_port=5002, console_port=5003):
        self.ui_port = ui_port
        self.artifact_store_port = artifact_store_port
        self.console_port = console_port
        mlflow.set_tracking_uri(f"http://localhost:{self.ui_port}")


    def start(self, quiet=True, python_version=None, mlflow_version=None):
        docker = create_client()
        _set_project_dir(os.getcwd())
        _set_ports(self.ui_port, self.artifact_store_port, self.console_port)

        if python_version and mlflow_version:
            _set_versions(python_=python_version, mlflow_=mlflow_version)
            docker.compose.build(quiet=quiet)
        elif python_version or mlflow_version:
            argument = "python_version" if python_version else "mlflow_version"
            message = f"Both python_version and mlflow_version must be provided for rebuilding the image. Only {argument} was provided."
            raise ValueError(message)

        # TODO: Change to docker compose start if the project already exists. 
        docker.compose.up(detach=True, quiet=quiet)


    def stop():
        docker = create_client()
        docker.compose.stop()


    def down(delete_all_data=False):
        docker = create_client()

        docker.compose.down(remove_orphans=True)

        if delete_all_data:
            pass



