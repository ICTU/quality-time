# Developing *Quality-time*

## Table of contents

- [Develop](#develop)
- [Test](#test)
- [Release](#release)
- [Software components](#software-components)

## Develop

Follow these instructions to run the software in hot-reload mode for easy development. Prerequisites are Python 3.8 and a recent version of Node.js (we test with the Long Term Support version of Node).

Clone this repository:

```console
git clone git@github.com:ICTU/quality-time.git
```

Open four terminals. In the first one, run the standard containers with docker-compose:

```console
docker-compose up database ldap phpldapadmin mongo-express testdata
```

Mongo-express is served at [http://localhost:8081](http://localhost:8081) and can be used to inspect and edit the database contents.

PHP-LDAP-admin is served at [http://localhost:3890](http://localhost:3890) and can be used to inspect and edit the LDAP database. Click login, check the "Anonymous" box and click "Authenticate" to login.

In the second terminal, run the server:

```console
cd components/server
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python src/quality_time_server.py
```

In the third terminal, run the collector:

```console
cd components/collector
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python src/quality_time_collector.py
```

In the fourth terminal, run the frontend:

```console
cd components/frontend
npm install
npm run start
```

The frontend is served at [http://localhost:3000](http://localhost:3000).

By default, there are three users defined in the LDAP database:

- User `admin` has password `admin`.
- User `Jane Doe` has user id `jadoe` and password `secret`.
- User `John Doe` has user id `jodoe` and password `secret`.

## Test

To run the unit tests and measure unit test coverage, change directory into the component folders, e.g.:

```console
cd components/server  # or components/collector
ci/unittest.sh
```

To run mypy and pylint:

```console
ci/quality.sh
```

To run the frontend unit tests:

```console
cd compontents/frontend
npm run test
```

## Release

See [Release README](../ci/README.md).

## Software components

![Components](components.png)

Quality-time consists of six components. Three standard components:

- A proxy (we use the [ICTU variant of Caddy](https://github.com/ICTU/caddy), but this can be replaced by another proxy if so desired) routing traffic from and to the user's browser,
- A database ([Mongo](https://www.mongodb.com)) for storing reports and measurements,
- A renderer (we use the [ICTU variant of url-to-pdf-api](https://github.com/ICTU/url-to-pdf-api) to export reports to PDF,

And three bespoke components:

- A [frontend](../components/frontend/README.md) serving the React UI,
- A [server](../components/server/README.md) serving the API,
- A [collector](../components/collector/README.md) to collect the measurements from the sources.

In addition, an LDAP server is expected to be available to authenticate users.

For testing purposes there are also [test data](../components/testdata/README.md) and an [LDAP-server](../components/ldap/README.md).
