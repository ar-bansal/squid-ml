import pytest
import os 
from pathlib import Path
from unittest.mock import patch, MagicMock
from python_on_whales import DockerClient
from operations import Server


@pytest.fixture
def server():
    return Server(
        "test_project", 
        ui_port=5001, 
        artifact_store_port=5002, 
        console_port=5003
        )


@pytest.fixture
def mock_compose():
    server_dir = Path(__file__).resolve().parent
    docker_compose_file = server_dir / "infra" / "docker-compose.yaml"
    return DockerClient(compose_files=[docker_compose_file])

# @pytest.fixture
# def mock_compose():
#     # Create a mock object for DockerClient
#     docker_client_mock = MagicMock()
#     return docker_client_mock


def test_init_set_env_variables(server):
    assert server.project_name == "test_project"
    # assert os.getenv("PROJECT_DIR") == os.getcwd()
    assert os.getenv("UI_PORT") == "5001"
    assert os.getenv("ARTIFACT_STORE_PORT") == "5002"
    assert os.getenv("CONSOLE_PORT") == "5003"
    assert os.getenv("UI_CONTAINER_NAME") == "test_project-mlops-ui"
    assert os.getenv("BACKEND_STORE_CONTAINER_NAME") == "test_project-mlops-backend_store"
    assert os.getenv("ARTIFACT_STORE_CONTAINER_NAME") == "test_project-mlops-artifact_store"

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


# @patch.object(mock_compose, "up")
# def test_start_valid_versions(mock_compose, server):
#     server.start(quiet=True, python_version="3.10", mlflow_version="2.18.0")
#     mock_compose.build.assert_called_once_with(quiet=True)
#     mock_compose.up.assert_called_once_with(detach=True, quiet=True)

# @patch("operations.DockerClient", new_callable=MagicMock)
# def test_start_valid_versions(mock_docker_client, mock_compose, server):
#     # Replace methods of DockerClient with the mock versions
#     mock_docker_client.return_value = mock_compose

#     # Call the method under test
#     server.start(quiet=True, python_version="3.10", mlflow_version="2.18.0")

#     # Assert that the mocked methods were called as expected
#     mock_compose.build.assert_called_once_with(quiet=True)
#     mock_compose.up.assert_called_once_with(detach=True, quiet=True)

# @patch("operations.DockerClient.compose.up")
# def test_start_up(mock_up, server):
#     server.start()
#     mock_up.assert_called_once_with(detach=True, quiet=True)


def test_start_up(server):
    server.start()
    
    client = server._create_docker_client()
    containers = client.ps()
    expected_containers = [
        "test_project-mlops-ui", 
        "test_project-mlops-artifact_store", 
        "test_project-mlops-backend_store"
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

# @patch.object(DockerClient, "compose")
# def test_stop(mock_compose, server):
#     server.stop()
#     mock_compose.stop.assert_called_once()

# @patch.object(DockerClient, "compose")
# def test_down(mock_compose, server):
#     server.down(quiet=True)
#     mock_compose.down.assert_called_once_with(remove_orphans=True, volumes=True, quiet=True)

# @patch.object(DockerClient, "compose")
# def test_down_delete_all_data(mock_compose, server):
#     # Test case with delete_all_data flag (though this doesn't do anything in the current code)
#     server.down(quiet=True, delete_all_data=True)
#     mock_compose.down.assert_called_once_with(remove_orphans=True, volumes=True, quiet=True)

def test_set_project_dir(server):
    server._set_project_dir("/my/project")
    assert os.getenv("PROJECT_DIR") == "/my/project"


def test_set_ports(server):
    server._set_ports()
    assert os.getenv("UI_PORT") == "5001"
    assert os.getenv("ARTIFACT_STORE_PORT") == "5002"
    assert os.getenv("CONSOLE_PORT") == "5003"


