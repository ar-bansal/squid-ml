import pytest
import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow import MlflowClient
from sklearn.linear_model import LinearRegression
from ..server.operations import Server
from ..ml_logging.loggers import SklearnLogger, PyTorchLogger
from .utils import *


@pytest.fixture(scope="module", autouse=True)
def infra_setup_and_teardown():
    server = Server(
        "test_project", 
        ui_port=5001, 
        artifact_store_port=5002, 
        console_port=5003
    )

    server.start()

    yield

    server.down(delete_all_data=True)


@pytest.fixture
def sklearn_logger():
    return SklearnLogger(logging_kwargs={"log_models": True})


@pytest.fixture
def pytorch_logger():
    return PyTorchLogger(save_graph=False, logging_kwargs={"log_models": True})

@pytest.fixture
def pytorch_logger_save_graph():
    return PyTorchLogger(save_graph=True, logging_kwargs={"log_models": True})


###################################### TRAIN FUNCTIONS ######################################
def dummy_train_function_sklearn(model, x, y, *args, **kwargs):
    model.fit(x, y)

    return model, {'accuracy': 0.95}  # Dummy model and metrics


def dummy_train_function_pytorch(model, datamodule, *args, **kwargs):
    trainer = create_trainer(3)

    trainer.fit(
        model=model, 
        datamodule=datamodule
        )
    
    return trainer.model, {
        "accuracy": 0.95, 
        # "confusion_matrix": pd.DataFrame(torch.rand((2, 2)), columns=["pred false", "pred true"])
    }


###################################### SKLEARN TESTING ######################################
def test_sklearn_logger_log_invalid(sklearn_logger):
    model = LinearRegression()
    x = np.random.rand(10, 10)
    y = np.random.rand(10, 1)

    logged_func = sklearn_logger.log(dummy_train_function_sklearn)
    with pytest.raises(ValueError, match=f"experiment_name must be specified as a kwarg when calling dummy_train_function_sklearn."):
        model, metrics = logged_func(model, x, y)

        
def test_sklearn_logger_log(sklearn_logger):
    # Log using the sklearn_logger
    model = LinearRegression()
    x = np.random.rand(10, 10)
    y = np.random.rand(10, 1)

    logged_func = sklearn_logger.log(dummy_train_function_sklearn)
    model, metrics = logged_func(model, x, y, experiment_name='test_sklearn')
    
    # Ensure the correct metrics were returned
    assert metrics['accuracy'] == 0.95


def test_mlflow_run_sklearn_logger():
    # Get the latest run
    client = MlflowClient(mlflow.get_tracking_uri())
    
    # Get the last completed run
    latest_run = client.search_runs(experiment_ids=[1])[0].to_dictionary()
    print(latest_run)
    artifact_uri = latest_run["info"]["artifact_uri"]
    model = mlflow.sklearn.load_model(artifact_uri + "/model")

    # Ensure the run is successful
    status = latest_run["info"]["status"]
    assert status == "FINISHED"
    # Assert that the model artifact exists
    assert type(model)  == LinearRegression    


###################################### PYTORCH TESTING ######################################
def test_pytorch_logger_save_graph_log_invalid(pytorch_logger_save_graph):
    model = NeuralNetwork()
    datamodule = TensorDataModule(
        X=torch.rand((20, 10)), 
        y=torch.randint(0, 2, (20, ))
    )

    logged_func = pytorch_logger_save_graph.log(dummy_train_function_pytorch)

    with pytest.raises(ValueError, match=f"experiment_name must be specified as a kwarg when calling dummy_train_function_pytorch."):
        model, metrics = logged_func(model, datamodule)

    with pytest.raises(ValueError, match=f"input_shape must be specified as a kwarg when calling dummy_train_function_pytorch if save_graph=True."):
        model, metrics = logged_func(model, datamodule, experiment_name="test_pytorch")


def test_pytorch_logger_log(pytorch_logger):
    model = NeuralNetwork()
    datamodule = TensorDataModule(
        X=torch.rand((20, 10)), 
        y=torch.randint(0, 2, (20, ))
    )

    logged_func = pytorch_logger.log(dummy_train_function_pytorch)
    model, metrics = logged_func(model, datamodule, experiment_name="test_pytorch")     

    assert metrics["accuracy"] == 0.95


def test_mlflow_run_pytorch_logger():
    client = MlflowClient(mlflow.get_tracking_uri())

    latest_run = client.search_runs(experiment_ids=[2])[0].to_dictionary()
    artifact_uri = latest_run["info"]["artifact_uri"]

    model = mlflow.pytorch.load_model(artifact_uri + "/model")

    status = latest_run["info"]["status"]
    assert status == "FINISHED"
    assert type(model) == NeuralNetwork
