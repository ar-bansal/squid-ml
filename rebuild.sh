#!/bin/bash

pip uninstall mlops -y && rm -rf dist/ mlops/mlops.egg-info/ mlops.egg-info/

python -m build 

pip install dist/mlops-0.1.0-py3-none-any.whl -q