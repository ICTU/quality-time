# Developing *Quality-time*

## Table of contents

- [Develop](#develop)
- [Test](#test)
- [Release](#release)

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

See [Release README](../ci/README.md).
