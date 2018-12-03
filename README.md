# Quality-time

[![Updates](https://pyup.io/repos/github/ICTU/quality-time/shield.svg)](https://pyup.io/repos/github/ICTU/quality-time/)

Quality report software for software development and maintenance. Alpha-stage currently. At the moment, a REST API
for collecting measurements from data sources is under construction.

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
- [Recent changes](#recent-changes)

## Installation

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

## Usage

To start the REST API server run:

`quality-time`

To test the API run:

`python tests/client.py`

## Recent changes

See the [change log](https://github.com/ICTU/quality-time/blob/master/CHANGELOG.md).
