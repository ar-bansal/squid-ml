from setuptools import setup, find_packages

setup(
    name="mlops",
    version="0.1.0",
    description="MLOps tools and utilities",
    author="Aryan Bansal",
    author_email="aryanbansal1710@gmail.com",
    url="https://github.com/ar-bansal/mlops",
    package_dir={"": "src"},  # Root of the packages is the src directory
    packages=find_packages(where="src"),  # Automatically find all packages under src
    include_package_data=True,  # Includes non-Python files specified in MANIFEST.in
    install_requires=[
        "mlflow",
        "boto3"
    ],
    entry_points={
        "console_scripts": [
            "mlops=src.cli_entrypoint:main",  # Enables CLI functionality
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
