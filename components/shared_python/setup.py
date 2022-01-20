"""Build information for shared python code."""
from setuptools import setup, find_packages

setup(
    name="shared-python",
    version="3.32.0-rc.4",
    packages=find_packages(include=["shared", "shared.*"]),
)
