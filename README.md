# mlops
Repository for MLOps infrastructure and MLflow logging.  

This repository works as a template for AI/ML and data science workflows. It aims to reduce the time and effort required to set up a project with the infrastructure and capabilities of logging ML experiments. 

## Features  
1. **Quickly set up MLOps infra**: This repo uses MLfLow for logging experiments, MinIO as an artifact store, and PostgreSQL as the backend for MLflow.  
2. **Easily log experiments and runs**: Use decorators to wrap the pipeline, which can then log the model training and evaluation metrics. Scikit-learn and PyTorch are supported as of Jan 16, 2025. 


## Usage  
1. Ensure that Docker is installed on the system.  
2. Initialize the infrastructure.
```
from server.operations import Server

# Default project_name is CWD's basename
tracking_server = Server(project_name="my-project")     

# Python and mlflow version need to be specified the first time.
tracking_server.start(
    quiet=False, 
    python_version="3.10", 
    mlflow_version="2.18.0"
    )      
```  

3. Use the logging decorators
```
from ml_logging.loggers import SklearnLogger, PyTorchLogger


def train_model(X_train, y_train, model):
    ...

def evaluate_model(X_test, y_test, model):
    ...


# Default logging_kwargs={}
@SklearnLogger(logging_kwargs={"serialization_format": mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE})
def run_pipeline(X_train, X_test, y_train, y_test, model, experiment_name="experiment1")
    # call train_model to get the model and training metrics
    # call evaluate_model to get the validation/test metrics

    # create a single dictionary with all the metrics that need to be logged, say all_metrics

    # return model and metrics to use mlflow.sklearn.autolog to log the model and metrics
    return model, metrics


@PyTorchLogger(save_graph=True)
def run_pipeline(model, train_dataloader, ..., experiment_name="dl-exp", input_shape=(8, 3, 32, 32))
    ...

    return model, metrics

```  