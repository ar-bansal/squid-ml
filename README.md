# mlops
Repository for MLOps infrastructure and MLflow logging.  

This repository works as a template for AI/ML and data science workflows. It aims to reduce the time and effort required to set up a project with the infrastructure and capabilities of logging ML experiments. 

## Features  
1. **Quickly set up MLOps infra**: This repo uses MLfLow for logging experiments, MinIO as an artifact store, and PostgreSQL as the backend for MLflow.  
2. **Easily log experiments and runs**: Use decorators to wrap the pipeline, which can then log the model training and evaluation metrics. Scikit-learn and PyTorch are supported as of now. 


## Usage  
1. Ensure that Docker is installed on the system.  
2. Initialize the infrastructure.
```
cd infra
MLFLOW_VERSION=2.18.0 PYTHON_VERSION=3.10 docker compose -p <PROJECT_NAME> up -d --build
```  
The `MLFLOW_VERSION` and `PYTHON_VERSION` variables only need to be set the first time, or when using the `--build` flag. Ensure that the local environment's MLflow and python versions are used here. For MLflow, provide the complete version. For python, provide upto the minor version. 

For bringing up the infra after it has been initialized before, use the following command: 
```
docker compose -p <PROJECT_NAME> up -d
```
3. Use the logging decorators
```
from ml_logging import log_sklearn, log_pytorch


def train_model(X_train, y_train, model):
    ...

def evaluate_model(X_test, y_test, model):
    ...

@log_sklearn
def run_pipeline(X_train, X_test, y_train, y_test, model, experiment_name="experiment1")
    # call train_model to get the model and training metrics
    # call evaluate_model to get the validation/test metrics

    # create a single dictionary with all the metrics that need to be logged, say all_metrics

    # return model and metrics to use mlflow.sklearn.autolog to log the model and metrics
    return model, metrics
```  

If using an EC2 instance to host the tracking server, use `server.sh` to start and stop the EC2 VM before and after the experiments to ensure that the tracking server is only running when a model is actually being trained. Also, use `ml_logging.get_tracking_uri()` to fetch the tracking server's URI. 