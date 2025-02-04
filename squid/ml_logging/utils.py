import os
from pandas import DataFrame
import mlflow
import mlflow.models
import mlflow.sklearn
import mlflow.pytorch
from torchview import draw_graph


def _start_run(func, *args, **kwargs):
    """
    Start an MLflow run and log any metrics returned by func.
    """
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        model, metrics = func(*args, **kwargs)
        for metric_name, metric_val in metrics.items():
            if isinstance(metric_val, DataFrame):
                filename = metric_name + ".csv"
                metric_val.to_csv(filename, index=False)
                mlflow.log_artifact(filename)
                os.remove(filename)
            else:
                mlflow.log_metric(metric_name, metric_val)

    return model, metrics, run_id


def _convert_name_to_prefix(experiment_name: str):
    """
    Convert experiment_name into a valid prefix that can be used in a MinIO server.

    Valid prefixes will only contain alphanumeric characters and hyphens. 
    """
    return ''.join(['-' if not c.isalnum() else c for c in experiment_name])


def _get_experiment_id(experiment_name: str):
    """
    Retrieve the experiment ID for the experiment name. Create 
    a new experiment if it does not exist.

    Parameters:
        - experiment_name (str): The MLflow experiment name.
    """
    artifact_location = _convert_name_to_prefix(experiment_name)

    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
    except AttributeError:
        experiment_id = mlflow.create_experiment(experiment_name, artifact_location=f"mlflow-artifacts:/{artifact_location}")

    return experiment_id


def _save_pytorch_model_graph(model, input_shape, run_id):
    filename = model.__class__.__name__
    model_graph = draw_graph(
        model, 
        input_size=input_shape, 
        device="meta", 
        expand_nested=True, 
        save_graph=True, 
        filename=filename
    )
    image_name = filename + ".png"
    mlflow.log_artifact(image_name, run_id=run_id)
    os.remove(image_name)
    os.remove(filename)
