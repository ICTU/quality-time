# Quality-time

[![Updates](https://pyup.io/repos/github/ICTU/quality-time/shield.svg)](https://pyup.io/repos/github/ICTU/quality-time/)

Quality report software for software development and maintenance. Alpha-stage currently. At the moment, a REST API
for collecting measurements from data sources is under construction.

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
- [Recent changes](#recent-changes)

## Installation

### From source

*Quality-time* requires Python 3.7 or newer.

There's no release yet, so you have to run from sources for the time being.

Clone this repository:

`git clone git@github.com:ICTU/quality-time.git`

Create a virtual environment:

`python3 -m venv .venv`

Install the dependencies:

`pip install -r requirements.txt -r requirements-dev.txt`

Start development mode:

`python setup.py develop`

### Using Docker

Alternatively, create a Docker image:

`docker build -t ictu/quality-time .`

## Usage

### From source

To start the REST API server run:

`quality-time`

### Using Docker

To start the Docker container:

`docker run -p 8080:8080 -ti ictu/quality-time`

### Test

To test the API run:

`python tests/client.py`

## Recent changes

See the [change log](https://github.com/ICTU/quality-time/blob/master/CHANGELOG.md).
