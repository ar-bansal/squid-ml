import pytest
import numpy as np
import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from sklearn.linear_model import LinearRegression
from server.operations import Server
from ml_logging.loggers import SklearnLogger

@pytest.fixture
def server():
    return Server(
        "test_project", 
        ui_port=5001, 
        artifact_store_port=5002, 
        console_port=5003
    )

@pytest.fixture
def sklearn_logger():
    return SklearnLogger(logging_kwargs={'log_models': True})

def dummy_train_function(model, x, y, *args, **kwargs):
    model.fit(x, y)

    return model, {'accuracy': 0.95}  # Dummy model and metrics


def test_sklearn_logger_log(server, sklearn_logger):
    # Start the server
    server.start()

    # Log using the sklearn_logger
    model = LinearRegression()
    x = np.random.rand(10, 10)
    y = np.random.rand(10, 1)

    logged_func = sklearn_logger.log(dummy_train_function)
    model, metrics = logged_func(model, x, y, experiment_name='test_experiment')
    
    # Ensure the correct metrics were returned
    assert metrics['accuracy'] == 0.95


def test_mlflow_run_sklearn_logger(server):
    # # Start the server
    server.start()

    # Get the latest run
    client = MlflowClient(mlflow.get_tracking_uri())
    
    # Get the last completed run
    latest_run = client.search_runs(experiment_ids=[1])[0].to_dictionary()
    model = mlflow.sklearn.load_model(latest_run.info.artifact_uri + "/model")

    # Ensure the run is successful
    assert latest_run.info.status == "FINISHED"
    # Assert that the model artifact exists
    assert type(model)  == LinearRegression