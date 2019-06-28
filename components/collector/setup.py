"""Setuptools setup script for Quality-time collector."""

from setuptools import find_packages, setup


setup(
    name="Quality-time collector",
    version="0.2.2",
    description="Quality report metrics collector.",
    author="Frank Niessink",
    author_email="frank.niessink@ictu.nl",
    url="https://github.com/ICTU/quality-time",
    license="Apache License, Version 2.0",
    python_requires=">=3.7",
    install_requires=[],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "quality-time-collector=src:collect"
        ],
    },
    zip_safe=True)
