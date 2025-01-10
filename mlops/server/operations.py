import os
import shutil
from python_on_whales import DockerClient


server_dir = os.path.dirname(os.path.abspath(__file__))
infra_dir = os.path.join(server_dir, "infra")
COMPOSE_FILE = os.path.join(infra_dir, "docker-compose.yaml")
COMPOSE_ENV_FILE = os.path.join(infra_dir, ".env")
docker = DockerClient(compose_files=[COMPOSE_FILE], compose_env_files=[COMPOSE_ENV_FILE])

# Set the volume mounting directory as <user PWD>/mlops_data
MLOPS_DATA_DIR = os.path.join(os.getcwd(), "mlops_data")
os.makedirs(MLOPS_DATA_DIR, exist_ok=True)
os.environ["MLOPS_VOLUME_MOUNT_DIR"] = MLOPS_DATA_DIR


def start(quiet: bool=True, python_version: str=None, mlflow_version: str=None):
    """
    Create and start the tracking server, backend store, and artifact store containers. 

    If python_version and mlflow_version are provided, a new version of the mlflow image
    is built using the Python and MLflow version. 
    """
    # Rebuild if both python_version and mlflow_version are passed. 
    if python_version and mlflow_version:
        docker.compose.build(build_args={
            "python_version": python_version, 
            "mlflow_version": mlflow_version
        }, 
        quiet=quiet)

    elif python_version or mlflow_version:
        # Skip rebuild
        argument = "python_version" if python_version else "mlflow_version"
        print(f"Skipping rebuild as {argument} was not provided. Provide both python_version and mlflow_version to rebuild the mlflow image.")
    
    # Start containers
    docker.compose.up(detach=True, pull="missing", quiet=quiet)


def stop():
    """
    Stop the running containers. 
    """
    docker.compose.stop()


def _delete_all_data(path):
    if os.path.exists(path):
        try:
            os.chmod(path, 0o777)
            shutil.rmtree(path)
        except Exception as e:
            print("Could not delete the mounted volumes due to the following error. Please delete them manually.")
            print(e)

def destroy(delete_all_data=False):
    docker.compose.down(remove_orphans=True)

    if delete_all_data:
        _delete_all_data(MLOPS_DATA_DIR)