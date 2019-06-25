# Quality-time

[![Build Status](https://travis-ci.org/ICTU/quality-time.svg?branch=master)](https://travis-ci.org/ICTU/quality-time)

Quality report software for software development and maintenance. *Quality-time* continuously collects measurement data from sources such as Gitlab, SonarQube, Jira, Azure DevOps, and OWASP Dependency Check, to provide an overview of the quality of software products and projects. It does so by comparing measurement data with metric targets and informing development teams about the metrics that need improvement actions.

*Quality-time* is **Alpha-stage** currently. We hope to have a beta-version ready by the 1st of July, 2019.

Technically, *Quality-time* consists of a Mongo database server, an LDAP server, a API-server written in Python, a metrics data collector also written in Python, and a React frontend. One of its purposes is to become a successor of [HQ](https://github.com/ICTU/quality-report).

Users can add and configure reports, metrics, and sources (such as SonarQube and Jira) in the frontend. The collector collects metrics data from the configured lmetric sources. It posts the measurements to the server which in turn stores them in the database. The frontend calls the server to get the reports and the measurements and presents them to the user.

## Table of contents

- [Screenshots](#screenshots)
- [Features](#features)
- [Installation](#installation)
- [Test](#test)
- [Deployment](#deployment)
- [Recent changes](#recent-changes)

Also see the [user manual](USAGE.md).

## Screenshots

Some screenshots to wet your appetite.

### Projects dashboard

*Quality-time* shows a summary of the projects on its landing page:

![Screenshot](screenshots/projects_dashboard.png)

### Metrics overview

For each metric, *Quality-time* displays the key data:

![Screenshot](screenshots/metrics.png)

### Metric details

Users can expand the metrics to see and configure the metric details and manage false positives:

![Screenshot](screenshots/metric_details.png)

## Features

Implemented features so far include:

- Rubost data collection (the collector should never fail, even in the face of misconfigured or unavailable sources).
- Measurement history is kept in a database, allowing for time travel.
- Easy report configuration via the UI.
- Multiple reports in one *Quality-time* instance.
- The possibility to use HQ as a metric source.
- Simple/naive LDAP-integration.
- Generic false-positive management.
- Metric tags can be used to summarize metrics with the same tag across subjects, e.g. to summarize all security metrics.

For more plans, see the issue tracker.

## Trying it out

*Quality-time* requires Docker and Docker-compose.

There's no release yet, so you have to run from sources for the time being.

Clone this repository:

```console
git clone git@github.com:ICTU/quality-time.git
```

Build the containers:

```console
docker-compose build
```

Start the containers:

```console
docker-compose up
```

The frontend is served at [http://localhost:5000](http://localhost:5000).

By default, there is one user defined. Use username `admin` and password `admin` to log in.

## Develop

Follow these instructions to run the software in hot-reload mode for easy development. Prerequisites are Python 3.7 and a recent version of Node.js (we test with the Long Term Support version of Node).

Clone this repository:

```console
git clone git@github.com:ICTU/quality-time.git
```

Open four terminals. In the first one, run the standard containers with docker-compose:

```console
docker-compose up database ldap mongo-express testdata
```

Mongo-express is served at [http://localhost:8081](http://localhost:8081) and can be used to inspect and edit the database contents.

In the second terminal, run the server:

```console
cd components/server
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python setup.py develop
quality-time-server
```

In the third terminal, run the collector:

```console
cd components/collector
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python setup.py develop
quality-time-collector
```

In the fourth temrinal, run the frontend:

```console
cd components/frontend
npm install
npm run start
```

The frontend is served at [http://localhost:3000](http://localhost:3000).

By default, there is one user defined. Use username `admin` and password `admin` to log in.

## Test

To run the unit tests and measure unit test coverage, change directory into the component folders, e.g.:

```console
cd compontents/server
ci/unittest.sh
```

To run mypy and pylint:

```console
ci/quality.sh
```

To run the frontend unit tests (which are unfortunately mostly missing at the moment):

```console
cd compontents/frontend
npm run test
```

To run the frontend UI tests (automated regression test):

```console
cd components/art
npm install --save-dev
npx cypress run
```

Cypress stores screenshots (if a test fails) and video in `components/art/cypress/screenshots` and `components/art/cypress/videos`.

## Release

To release *Quality-time*, follow these steps:

```console
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
ci/release.py major|minor|patch
```

The `release.py` script will bump the version numbers, commit the changes, push the commit, tag the commit, and push the tag to Github.

## Deployment

(To be completed)

### LDAP

To configure a LDAP server to authenticate users with, set the `LDAP_URL` and `LDAP_ROOT_DN` environment variables. When running locally, this can be done in the shell:

```console
$ export LDAP_URL="ldap://ldap.example.org:389"
$ export LDAP_ROOT_DN="dc=example,dc=org"
$ quality-report-server
INFO:root:Connected to database: Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'quality_time_db')
INFO:root:Measurements collection has 108 measurements
INFO:root:Initializing LDAP server at ldap://ldap.example.org:389
...
```

When using docker-compose, add the LDAP environment variables to the server section:

```yaml
...
server:
    image: docker-registry.example.org:5000/ictu/quality-time-server
    ports:
    - "8080:8080"
    environment:
    - FRONTEND_URL=http://www.quality-time.example.org:5000
    - SERVER_URL=http://server.quality-time.example.org:8080
    - DATABASE_URL=mongodb://root:root@database:27017
    - LDAP_URL=ldap://ldap.example.org:389
    - LDAP_ROOT_DN="dc=example,dc=org"
```

Users can only use their canonical name (`cn`) to login at the moment.

## Recent changes

The [change log](https://github.com/ICTU/quality-time/blob/master/CHANGELOG.md) will not be maintained until after the first release.
