import pytest
import numpy as np
import mlflow
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
    try:
        assert metrics['accuracy'] == 0.95
        assert isinstance(model, object)
    
    finally:
        server.stop()



def test_mlflow_run(server):
    # # Start the server
    server.start()

    # Assuming the tracking URI has been set correctly
    tracking_uri = mlflow.get_tracking_uri()
    print(f"MLflow Tracking URI: {tracking_uri}")

    # Get the latest run
    client = MlflowClient(tracking_uri)
    
    # Get the last completed run
    latest_run = client.search_runs(
        experiment_ids=[0, 1], 
        order_by=["start_time desc"], 
        max_results=1)[0]
    

    # Check if a model artifact exists
    run_id = latest_run.info.run_id
    artifacts = client.list_artifacts(run_id)
    print(artifacts)
    model_artifact = None
    
    for artifact in artifacts:
        if 'model' in artifact.path.lower(): 
            model_artifact = artifact
            break

    try:
        # Ensure the run is successful
        assert latest_run.info.status == "FINISHED"
        # Assert that the model artifact exists
        assert model_artifact is not None
    finally:

        # Shutdown the server
        server.down(delete_all_data=True)