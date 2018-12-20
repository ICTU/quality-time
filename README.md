# Quality-time

[![Updates](https://pyup.io/repos/github/ICTU/quality-time/shield.svg)](https://pyup.io/repos/github/ICTU/quality-time/)

Quality report software for software development and maintenance. Alpha-stage currently. At the moment, *Quality-time* consists of a simple backend API and a simple React frontend. Its main purpose is to experiment with features that may or may not land in [HQ](https://github.com/ICTU/quality-report).

The backend API is called by the frontend to collect measurements from different data sources. Its purpose is to hide the complexity of the different metric sources behind a facade. The frontend asks the backend for a report configuration and then uses the backend API to collect the metrics.

Planned features/experiments include:

- [X] Simpler and robust data collection
- [ ] Scheduled data collection
- [ ] History integrated in the API and report
- [ ] Time travel
- [ ] Simpler report configuration (YAML?)
- [ ] A different representation of metrics than a boring table. Maybe big cards for metrics that demand attention and small for metrics that are ok.

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
- [Test](#test)
- [Recent changes](#recent-changes)

## Installation

The *Quality-time* backend requires Python 3.7 or newer.

There's no release yet, so you have to run from sources for the time being.

Clone this repository:

`git clone git@github.com:ICTU/quality-time.git`

Create a virtual environment:

`python3 -m venv .venv`

Install the dependencies:

`pip install -r requirements.txt -r requirements-dev.txt`

Start development mode:

`python setup.py develop`

Optionally, to create a Docker image for the backend:

`docker build -t ictu/quality-time .`

The frontend needs Node and npm.

## Usage

To start the back end run:

`quality-time-facade`

Or, start the back end Docker container:

`docker run -p 8080:8080 -ti ictu/quality-time`

To start the application server, run:

`cd quality-time-app || npm start`

## Test

To run the unit tests and measure unit test coverage:

`ci/unittest.sh`

To run mypy and pylint:

`ci/quality.sh`

## Recent changes

See the [change log](https://github.com/ICTU/quality-time/blob/master/CHANGELOG.md).
