from mlflow import start_run, log_artifact, log_metric, get_experiment_by_name, create_experiment, set_experiment as set_exp
# import mlflow
from pandas import DataFrame
from functools import wraps



def __convert_name_to_prefix(experiment_name: str):
    """
    Convert experiment_name into a valid prefix that can be used in a MinIO server.

    Valid prefixes will only contain alphanumeric characters and hyphens. 
    """
    return ''.join(['-' if not c.isalnum() else c for c in experiment_name])


def _parametrized(dec):
    """
    Decorator to parametrize another decorator. 
    """
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer


def _start_run(func, *args, **kwargs):
    """
    Start an MLFlow run and log any metrics returned by func.
    """
    with start_run():
        model, metrics = func(*args, **kwargs)
        for metric_name, metric_val in metrics.items():
            if isinstance(metric_val, DataFrame):
                metric_val.to_csv(metric_name + ".csv", index=False)
                log_artifact(metric_name + ".csv")
            else:
                log_metric(metric_name, metric_val)

    return model, metrics


def _get_experiment_id(experiment_name: str):
    """
    Retrieve the experiment ID for the experiment name. Create 
    a new experiment if it does not exist.

    Parameters:
        - experiment_name (str): The MLFlow experiment name.
    """
    artifact_location = __convert_name_to_prefix(experiment_name)

    try:
        experiment = get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
    except AttributeError:
        experiment_id = create_experiment(experiment_name, artifact_location=f"mlflow-artifacts:/{artifact_location}")

    return experiment_id


def set_experiment(experiment_name):
    # experiment_name = kwargs["experiment_name"]
    experiment_id = _get_experiment_id(experiment_name)
    set_exp(experiment_id=experiment_id)


# def _create_logging_decorator(autolog):
#     def logging_decorator(func, **logging_kwargs):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             experiment_name = kwargs["experiment_name"]
#             experiment_id = _get_experiment_id(experiment_name)
#             set_experiment(experiment_id)

#             # Enable autologging with specified parameters
#             autolog(**logging_kwargs)

#             # Run the original function
#             model, metrics = _start_run(func, *args, **kwargs)

#             # Disable autologging after the run
#             autolog(disable=True)
#             return model, metrics
#         return wrapper
#     return logging_decorator