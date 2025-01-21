import pytest
import os 
from operations import Server


@pytest.fixture
def server():
    return Server(
        "test_project", 
        ui_port=5001, 
        artifact_store_port=5002, 
        console_port=5003
        )


def test_init_set_env_variables(server):
    assert os.getenv("PROJECT_NAME") == "test_project"
    assert os.getenv("UI_PORT") == "5001"
    assert os.getenv("ARTIFACT_STORE_PORT") == "5002"
    assert os.getenv("CONSOLE_PORT") == "5003"

def test_set_versions_valid(server):
    server._set_versions(python_="3.10", mlflow_="2.18.0")
    assert os.getenv("PYTHON_VERSION") == "3.10"
    assert os.getenv("MLFLOW_VERSION") == "2.18.0"

def test_set_version_invalid_python(server):
    python_versions = ["3.10.0", "3.abc"]
    for ver in python_versions:
        with pytest.raises(ValueError, match=f"Python version must be of the form '<major>.<minor>', like '3.10'. Provided '{ver}'"):
            server._set_versions(python_=ver, mlflow_="2.18.0")

def test_set_version_invalid_mlflow(server):
    mlflow_versions = ["2.18", "2.abc.0"] 
    for ver in mlflow_versions:
        with pytest.raises(ValueError, match=f"MLflow version must be of the form '<major>.<minor>.<patch>', like '2.18.0'. Provided '{ver}'"):
            server._set_versions(python_="3.10", mlflow_=ver)


def test_start_up(server):
    server.start()
    
    client = server._create_docker_client()
    containers = client.ps()
    expected_containers = [
        "test_project-mlops-ui", 
        "test_project-mlops-artifact-store", 
        "test_project-mlops-backend-store"
    ]

    container_names = set([c.name for c in containers])
    
    for expected_c in expected_containers:
        assert expected_c in container_names
    
    server.down()


# def test_server_build(server):
#     server.start(python_version="3.10", mlflow_version="2.18.0")

#     client = server._create_docker_client()

#     client.image.exists("mlflow_server:latest")

#     server.down()
    

def test_start_invalid_versions(server):
    with pytest.raises(ValueError, match="Both python_version and mlflow_version must be provided for rebuilding the image. Only python_version was provided."):
        server.start(python_version="3.10", mlflow_version="")

    with pytest.raises(ValueError, match="Both python_version and mlflow_version must be provided for rebuilding the image. Only mlflow_version was provided."):
        server.start(python_version="", mlflow_version="2.18.0")


def test_set_project_dir(server):
    server._set_project_dir("/my/project")
    assert os.getenv("PROJECT_DIR") == "/my/project"
