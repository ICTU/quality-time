"""Setuptools setup script for Quality-time server."""

from setuptools import find_packages, setup


setup(
    name="Quality-time server",
    version="0.5.1",
    description="Quality report data server.",
    author="Frank Niessink",
    author_email="frank.niessink@ictu.nl",
    url="https://github.com/ICTU/quality-time",
    license="Apache License, Version 2.0",
    python_requires=">=3.7",
    install_requires=[],
    packages=find_packages(),
    zip_safe=True)

