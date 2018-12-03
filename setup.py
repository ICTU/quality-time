"""Setuptools setup script for Quality-time."""

from setuptools import setup, find_packages

import quality_time


setup(
    name=quality_time.__title__,
    version=quality_time.__version__,
    description="Quality report application.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Frank Niessink",
    author_email="frank.niessink@ictu.nl",
    url="https://github.com/ICTU/quality-time",
    license="Apache License, Version 2.0",
    python_requires=">=3.7",
    install_requires=[],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "quality-time=quality_time:quality_time",
        ],
    },
    zip_safe=True,
    #test_suite="tests",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "'Topic :: Software Development :: Quality Assurance"],
    keywords=[])
