from functools import wraps
import mlflow
import mlflow.sklearn
import mlflow.pytorch
from .mlflow_utils import _start_run, _get_experiment_id, _save_pytorch_model_graph


class MLFlowLogger:
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
            self.post_run(self, model, metrics)

            # Disable autologging
            self.autolog(disable=True)
            return model, metrics

        return wrapper

    def post_run(self, model, metrics):
        """
        Hook to perform actions after the run. To be overridden by subclasses.

        Parameters:
        - model: The trained model.
        - metrics (dict): The logged metrics.
        - kwargs (dict): Additional arguments passed to the training function.
        """
        pass


class PyTorchLogger(MLFlowLogger):
    def __init__(self, save_graph=False, logging_kwargs={}):
        """
        A class for creating PyTorch-specific decorators for logging with MLflow.
        """
        super().__init__(
            autolog=mlflow.pytorch.autolog, 
            logging_kwargs=logging_kwargs
            )
        self.save_graph = save_graph

    def post_run(self, model, metrics):
        """
        Save the PyTorch model graph after the run if save_graph is True.

        Parameters:
        - model: The trained PyTorch model.
        - metrics (dict): The logged metrics.
        """
        # Save the model graph only if save_graph is True
        if self.save_graph:
            _save_pytorch_model_graph(model, self._latest_run_id)



class SklearnLogger(MLFlowLogger):
    def __init__(self, logging_kwargs={}):
        """
        A class for creating Scikit-learn-specific decorators for logging with MLflow.
        """
        super().__init__(
            autolog=mlflow.sklearn.autolog, 
            logging_kwargs=logging_kwargs
            )