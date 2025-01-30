from functools import wraps
import mlflow
from mlflow import MlflowClient
import mlflow.sklearn
import mlflow.pytorch
from .mlflow_utils import _start_run, _get_experiment_id, _save_pytorch_model_graph


class MLFlowLogger:
    """
    Base class for implementing autologging via mlflow.<flavor>.autolog
    """
    def __init__(self, autolog, logging_kwargs={}):
        """
        A base class to create decorators for logging model training with MLflow.

        Parameters:
        - autolog: The MLflow autolog function for the framework.
        """
        self.autolog = autolog
        self.logging_kwargs = logging_kwargs
        self._latest_run_id = None


    def log(self, func):
        """
        The decorator function for logging model training with MLflow.

        Returns:
        - A wrapped function that logs the training process with MLflow.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            wrapped_func_name = func.__name__
            self._sanity_check(wrapped_func_name, *args, **kwargs)

            # Set the experiment
            experiment_name = kwargs["experiment_name"]
            experiment_id = _get_experiment_id(experiment_name)
            mlflow.set_experiment(experiment_id=experiment_id)

            # Enable autologging
            self.autolog(**self.logging_kwargs)

            # Run the training function
            model, metrics, run_id = _start_run(func, *args, **kwargs)

            # Post-run hooks
            self._latest_run_id = run_id
            self.post_run(model, metrics, *args, **kwargs)

            # Disable autologging
            self.autolog(disable=True)
            return model, metrics

        return wrapper


    def _sanity_check(self, wrapped_func_name, *args, **kwargs):
        """
        Hook to perform checks before the run. Ensures that the script fails 
        before the run is started, if something is wrong. 
        """
        if not kwargs.get("experiment_name"):
            raise ValueError(f"experiment_name must be specified as a kwarg when calling {wrapped_func_name}.")


    def post_run(self, model, metrics, *args, **kwargs):
        """
        Hook to perform actions after the run. To be overridden by subclasses.

        Parameters:
        - model: The trained model.
        - metrics (dict): The logged metrics.
        - kwargs (dict): Additional arguments passed to the training function.
        """
        pass


class PyTorchLogger(MLFlowLogger):
    """
    Class for logging PyTorch models via mlflow.pytorch.autolog.
    """
    def __init__(self, save_graph=False, logging_kwargs={}):
        """
        A class for creating PyTorch-specific decorators for logging with MLflow.
        """
        super().__init__(
            autolog=mlflow.pytorch.autolog, 
            logging_kwargs=logging_kwargs
            )
        self.save_graph = save_graph


    def _sanity_check(self, wrapped_func_name, *args, **kwargs):
        super()._sanity_check(wrapped_func_name, *args, **kwargs)
        if self.save_graph:
            if not kwargs.get("input_shape"):
                raise ValueError(f"input_shape must be specified as a kwarg when calling {wrapped_func_name} if save_graph=True.")


    def post_run(self, model, metrics, *args, **kwargs):
        """
        Save the PyTorch model graph after the run if save_graph is True.

        Parameters:
        - model: The trained PyTorch model.
        - metrics (dict): The logged metrics.
        """
        # Save the model graph only if save_graph is True
        mlflow_client = MlflowClient(mlflow.get_tracking_uri())

        estimator_tags = {
            "estimator_class": str(model.__class__).split("'")[1], 
            "estimator_name": model.__class__.__name__
        }

        for k, v in estimator_tags.items():
            mlflow_client.set_tag(run_id=self._latest_run_id, key=k, value=v)

        if self.save_graph:
            _save_pytorch_model_graph(model, input_shape=kwargs["input_shape"], run_id=self._latest_run_id)



class SklearnLogger(MLFlowLogger):
    """
    Class for logging sklearn models via mlflow.sklearn.autolog.
    """
    def __init__(self, logging_kwargs={}):
        """
        A class for creating Scikit-learn-specific decorators for logging with MLflow.
        """
        super().__init__(
            autolog=mlflow.sklearn.autolog, 
            logging_kwargs=logging_kwargs
            )