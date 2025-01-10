# import mlflow
import mlflow.sklearn
import mlflow.pytorch
from functools import wraps
import pathlib
import os
from ._decorator_helpers import set_experiment, _parametrized, _get_experiment_id, _start_run


# def get_tracking_uri(instance_id: str=None):
#     if not instance_id:
#         server_ip = "localhost"
#     else:
#         server_ip = _get_public_ip(instance_id)
    
#     return f"http://{server_ip}"    

def get_project_directory():
    # This gives the directory where the package is being imported
    package_directory = pathlib.Path(__file__).resolve().parent
    
    # Assuming the package is within the project directory structure, go up one level
    project_directory = package_directory.parent
    return project_directory


@_parametrized
def log_sklearn(func, logging_kwargs):
    """
    Decorator for logging model parameters, metrics, and the model artifact to MLflow.

    Parameters: 
        - experiment_name (str): The MLFlow experiment name.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Set the experiment
        set_experiment(experiment_name=kwargs["experiment_name"])
        # experiment_name = kwargs["experiment_name"]
        # experiment_id = _get_experiment_id(experiment_name)
        # mlflow.set_experiment(experiment_id=experiment_id)

        mlflow.sklearn.autolog(**logging_kwargs)
        model, metrics = _start_run(func, *args, **kwargs)

        mlflow.sklearn.autolog(disable=True)
        return model, metrics
    return wrapper


@_parametrized
def log_pytorch(func, logging_kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        set_experiment(experiment_name=kwargs["experiment_name"])
        # experiment_name = kwargs["experiment_name"]
        # experiment_id = _get_experiment_id(experiment_name)
        # mlflow.set_experiment(experiment_id=experiment_id)

        mlflow.pytorch.autolog(**logging_kwargs)
        model, metrics = _start_run(func, *args, **kwargs)

        mlflow.pytorch.autolog(disable=True)
        return model, metrics
    return wrapper
