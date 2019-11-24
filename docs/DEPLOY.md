# Deploying *Quality-time*

Quality-time consists of containers that together form the application: a proxy that routes incoming traffic to either the frontend container to serve the React frontend and static resources or the server container that serves the REST API. The database container runs a Mongo database server and the collector container collects the measurement data for the metrics.

## Docker-compositions

This document assumes docker-compose is used to deploy the containers. The docker folder of this repo contains different compose files for running Quality-time in development, continuous integration, staging, and production environments, see the [docker folder](../docker).

## Configuring LDAP

To configure an LDAP server to authenticate users with, set the `LDAP_URL`, `LDAP_ROOT_DN`, `LDAP_LOOKUP_USER_DN`, `LDAP_LOOKUP_USER_PASSWORD`, and `LDAP_SEARCH_FILTER` environment variables. When running locally, this can be done in the shell:

<!-- markdownlint-disable commands-show-output -->

```console
$ export LDAP_URL="ldap://ldap.example.org:389"
$ export LDAP_ROOT_DN="dc=example,dc=org"
$ export LDAP_LOOKUP_USER_DN="cn=lookup_user,dc=example,dc=org"
$ export LDAP_LOOKUP_USER_PASSWORD="secret"
$ export LDAP_SEARCH_FILTER='(|(uid=$username)(cn=$username))'  # Single quotes to prevent the shell from expanding the username variable
$ cd components/server
$ python src/quality_report_server.py
INFO:root:Connected to database: Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'quality_time_db')
INFO:root:Measurements collection has 108 measurements
INFO:root:Initializing LDAP server at ldap://ldap.example.org:389
...
```

When using docker-compose, add the LDAP environment variables to the relevant env file in the [docker folder](../docker):

```bash
...
# Server
SERVER_PORT=5001
SERVER_HOST=server
DATABASE_URL=mongodb://root:root@database:27017
LDAP_URL=ldap://ldap.example.org:389
LDAP_ROOT_DN=dc=example,dc=org
LDAP_LOOKUP_USER_DN=cn=admin,dc=example,dc=org
LDAP_LOOKUP_USER_PASSWORD=admin
LDAP_SEARCH_FILTER=(|(uid=$username)(cn=$username))
LOAD_EXAMPLE_REPORTS=True
...
```

When using the `LDAP_SEARCH_FILTER` as shown above, users can use either their LDAP canonical name (`cn`) or their LDAP user id to login. The `$username` variable is filled by *Quality-time* at run time with the username that the user enters in the login dialog box.

See [https://ldap.com/ldap-filters/](https://ldap.com/ldap-filters/) for more information on LDAP filters.

## Settings per component

### Proxy

External traffic is routed by a Caddy reverse proxy (container name: proxy) to either the frontend container or the server container. The proxy listens on port 80. There's currently no environment variable to change the proxy port, but you can override the Caddy configurion in the `docker-compose.yml` if so desired.

### Frontend

The React UI is served by the frontend container, which runs at port 5000 by default. The Caddy reverse proxy routes external traffic that's not meant for the API to the frontend container.

To configure the frontend container port, set the `FRONTEND_PORT` environment variable. When running locally, this can be done in the shell:

```console
$ export FRONTEND_PORT=6000
$ cd components/frontend
$ npm start
> quality-time-app@0.20.0 start /Users/fniessink/workspace/quality-time/components/frontend
> react-scripts start
...
```

When using docker-compose add the `FRONTEND_PORT` environment variable to the relevant env file in the docker folder:

```bash
...
# Frontend
FRONTEND_PORT=6000
...
```

### Server

The API is accessible at the server container, running at port 5001 by default. The Caddy reverse proxy routes URLs that start with /api to the server.

To configure the server container port, set the `SERVER_PORT` environment variable. When running locally, this can be done in the shell:

```console
$ export SERVER_PORT=6001
$ cd components/server
$ python src/quality_time_server.py
INFO:root:Connected to database: Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'quality_time_db')
INFO:root:Database has 101 report documents and 467 measurement documents
INFO:root:Skipping loading the data model; it is unchanged
INFO:root:Skipping initializing reports overview; it already exists
...
```

When using docker-compose add the `SERVER_PORT` environment variable to the relevant env file in the docker folder:

```bash
...
# Server
SERVER_PORT=6001
...
```

### Collector

The collector contacts the server to see whether there's metrics that need to be measured and uses the server API to store the new measurements in the database. By default, the collector measures metrics whose configuration hasn't been changed every 15 minutes and sleeps 60 seconds in between measurements.

To configure the sleep duration and the measurement frequency, set the `COLLECTOR_SLEEP_DURATION` and `COLLECTOR_MEASUREMENT_FREQUENCY` environment variables. Both variables have seconds as unit. When running locally, this can be done in the shell:

```console
$ export COLLECTOR_SLEEP_DURATION=10
$ export COLLECTOR_MEASUREMENT_FREQUENCY=60
$ cd components/collector
$ python src/quality_report_collector.py
INFO:root:Loading data model...
INFO:root:Collecting...
```

When using docker-compose add the `COLLECTOR_SLEEP_DURATION` and `COLLECTOR_MEASUREMENT_FREQUENCY` environment variable to the relevant env file in the docker folder:

```bash
...
# Collector
COLLECTOR_SLEEP_DURATION=10
COLLECTOR_MEASUREMENT_FREQUENCY=60
...
```
