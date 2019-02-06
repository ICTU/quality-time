# Quality-time

Quality report software for software development and maintenance. Alpha-stage currently. At the moment, *Quality-time* consists of a Mongo database server, a server, a metrics data collector, and a React frontend. Its main purpose is to experiment with features for a successor of [HQ](https://github.com/ICTU/quality-report).

The collector collects metrics data from metric sources such as SonarQube and Jira. It posts the measurements to the server which in turn stores them in the database. The frontend calls the server to get the report and the measurements.

Planned features/experiments include:

- [X] Simpler and robust data collection.
- [X] Scheduled data collection.
- [X] History in a database, allowing for time travel.
- [X] Report configuration via the UI.
- [ ] A different representation of metrics than a boring table. Maybe big cards for metrics that demand attention and small for metrics that are ok.
- [ ] User authentication and role-based access.

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
- [Test](#test)
- [Recent changes](#recent-changes)

## Installation

*Quality-time* requires Docker and Docker-compose.

There's no release yet, so you have to run from sources for the time being.

Clone this repository:

`git clone git@github.com:ICTU/quality-time.git`

Build the containers:

`docker-compose build`

## Usage

Start the containers:

`docker-compose up`

The frontend is served at [http://localhost:5000](http://localhost:5000).

## Test

To run the unit tests and measure unit test coverage cd into the components, e.g. `cd compontents/server` and:

`ci/unittest.sh`

To run mypy and pylint:

`ci/quality.sh`

## Recent changes

See the [change log](https://github.com/ICTU/quality-time/blob/master/CHANGELOG.md).
