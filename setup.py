# lambda-image-processor/setup.py
"""
Setup script for the Lambda Image Processor Python package.

This script uses setuptools to define the package metadata, dependencies, and structure
for the AWS Lambda-based image processing application. It specifies the project name,
version, required libraries (e.g., Pillow), and includes the `app` module for packaging.
This utility resizes images and handles storage in Amazon S3 as part of a serverless workflow.

Usage:
    Run `python setup.py install` to install locally, or use `pip install .` for editable development installs.

Attributes:
    name (str): The distribution name of the package.
    version (str): The initial version of the package.
    packages (List[str]): Packages to include, filtered to 'app' and its submodules.
    install_requires (List[str]): Third-party packages required for runtime (e.g., Pillow).
    author (str): The author of the package.
    description (str): Short description for PyPI or package registries.
    classifiers (List[str]): Metadata tags for the package ecosystem.

Note:
    Ensure `app/__init__.py` exists to treat the directory as a valid Python package.
"""

from setuptools import setup, find_packages

setup(
    name="lambda_image_processor",
    version="0.1.0",
    packages=find_packages(include=["app", "app.*"]),
    install_requires=[
        "Pillow>=10.3.0"
    ],
    author="Your Name",
    description="AWS Lambda image processing utility (resizes and stores images in S3)",
    classifiers=[
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
)
