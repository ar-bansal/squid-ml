# Squid ML
A no-boilerplate, ease-to-use AI/ML experiment tracker. 

Do you find yourself spending more time setting up MLflow and the related infrastructure, compared to actually building models and data pipelines? Squid ML is here to help - log model training runs, artifacts, metrics, and more, using just 2 lines of code!

## Features  
1. **Quickly set up the tracking infrastructure**: This repo uses MLfLow for logging experiments, MinIO as an artifact store, and PostgreSQL as the backend store for MLflow.  
2. **Easily log experiments, runs, and artifacts**: Use decorators to wrap the pipeline, which can then log the model training and model evaluation metrics. `Scikit-learn`, `PyTorch`, and `TensorFlow` are supported as of Feb 4, 2025. 


## Usage
1. **Start the tracking server**: If you already have a tracking server set up, just call `mlflow.set_tracking_uri(...)` with your tracking URI.  
```
from squid import Server

# Default project_name is the current working directory's basename
tracking_server = Server(project_name="my-project")     

# Python and mlflow version need to be specified the first time.
tracking_server.start(
    quiet=False,                # Setting it to False will print logs on the terminal/cell
    python_version="3.10",      # Match with your environment's version for the best compatibility
    mlflow_version="2.18.0"     # Match with your environment's version for the best compatibility
    )      
```  

2. **Use the logging decorators**: While wrapping your pipeline, add `*args` and `**kwargs` as parameters. While calling the function, pass `experiment_name` as a keyword argument. 
```
from squid import SklearnLogger
from sklearn.linear_model import LinearRegression


def train_model(model, X_train, y_train):
    ...

def evaluate_model(model, X_test, y_test):
    ...


# Default logging_kwargs={}
# Refer to mlflow.sklearn.autolog's documentation for more logging_kwargs
sklearn_logger = SklearnLogger(
    logging_kwargs={
        "serialization_format": mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE
    }
)

@sklearn_logger.log
def run_pipeline(X_train, X_test, y_train, y_test, model, *args, **kwargs):
    # call train_model to get the model and training metrics
    # call evaluate_model to get the validation/test metrics

    # create a single dictionary with all the metrics that need to be logged

    # return model and metrics to use the decorator to log the model and metrics
    return model, metrics


def main():
    model = LinearRegression()
    X_train, X_test, y_train, y_test = ...

    model, metrics = run_pipeline(
        X_train, 
        X_test, 
        y_train, 
        y_test, 
        model, 
        experiment_name="my-experiment"
    )
```    


## Notes  
By default, the following values are used as username and passwords for the PostgreSQL and MinIO containers respectively: 
```
DB_USERNAME=dbuser
DB_PASSWORD=dbpassword

ARTIFACT_STORE_ACCESS_KEY=storeuser
ARTIFACT_STORE_SECRET_KEY=storepassword
```  

If you'd like to use different credentials for them, simply set the environment variables using `os`. 
```
import os 

os.environ["DB_USERNAME"] = mynewuser
os.environ["DB_PASSWORD"] = mynewpassword

os.environ["ARTIFACT_STORE_ACCESS_KEY"] = mynewuser
os.environ["ARTIFACT_STORE_SECRET_KEY"] = mynewpassword
```