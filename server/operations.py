import os
from python_on_whales import DockerClient
import mlflow


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
            os.environ["PYTHON_VERSION"] = python_version
            os.environ["MLFLOW_VERSION"] = mlflow_version
            docker.compose.build(quiet=quiet)

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



