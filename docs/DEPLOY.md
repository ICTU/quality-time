# Deploying *Quality-time*

Quality-time consists of containers that together form the application: a proxy that routes incoming traffic to either the frontend container to serve the React frontend and static resources or the server container that serves the REST API. The database container runs a Mongo database server and the collector container collects the measurement data for the metrics.

## Docker-composition

This document assumes docker-compose is used to deploy the containers. The docker folder of this repo contains different compose files for running Quality-time in development and continuous integration mode, see the [docker folder](../docker). You can use these compose files as basis for your own deployment configuration.

## Configuring LDAP

To configure an LDAP server to authenticate users with, set the `LDAP_URL`, `LDAP_ROOT_DN`, `LDAP_LOOKUP_USER_DN`, `LDAP_LOOKUP_USER_PASSWORD`, and `LDAP_SEARCH_FILTER` environment variables. Add the LDAP environment variables to the server service in the [compose file](../docker/docker-compose.yml):

```yaml
  server:
    environment:
      - LDAP_URL=ldap://ldap:389
      - LDAP_ROOT_DN=dc=example,dc=org
      - LDAP_LOOKUP_USER_DN=cn=admin,dc=example,dc=org
      - LDAP_LOOKUP_USER_PASSWORD=admin
      - LDAP_SEARCH_FILTER=(|(uid=$username)(cn=$username))
```

When using the `LDAP_SEARCH_FILTER` as shown above, users can use either their LDAP canonical name (`cn`) or their LDAP user id to login. The `$username` variable is filled by *Quality-time* at run time with the username that the user enters in the login dialog box.

See [https://ldap.com/ldap-filters/](https://ldap.com/ldap-filters/) for more information on LDAP filters.

## Settings per component

### Proxy

External traffic is routed by a Caddy reverse proxy (container name: www) to either the frontend container or the server container. The proxy listens on port 80. You can override the Caddy configuration in the [compose file](../docker/docker-compose.yml) if so desired.

### Frontend

The React UI is served by the frontend container, which runs at port 5000 by default. The Caddy reverse proxy routes external traffic that is not meant for the API to the frontend container. To configure the frontend container port, set the `FRONTEND_PORT` environment variable. Add the `FRONTEND_PORT` environment variable to both the proxy (www) and the frontend service:

```yaml
  www:
    environment:
      - FRONTEND_PORT=6000
  frontend:
    environment:
      - FRONTEND_PORT=6000
```

### Server

The API is accessible at the server container, running at port 5001 by default. The Caddy reverse proxy routes URLs that start with /api to the server. To configure the server container port, set the `SERVER_PORT` environment variable. Add the `SERVER_PORT` environment variable to both the server and the collector service:

```yaml
  server:
    environment:
      - SERVER_PORT=6001
  collector:
    environment:
      - SERVER_PORT=6001
```

### Collector

The collector contacts the server to see whether there's metrics that need to be measured and uses the server API to store the new measurements in the database. By default, the collector measures metrics whose configuration hasn't been changed every 15 minutes and sleeps 60 seconds in between measurements.

To configure the sleep duration and the measurement frequency, set the `COLLECTOR_SLEEP_DURATION` and `COLLECTOR_MEASUREMENT_FREQUENCY` environment variables. Both variables have seconds as unit. Add the `COLLECTOR_SLEEP_DURATION` and `COLLECTOR_MEASUREMENT_FREQUENCY` environment variables to collector service:

```yaml
  collector:
    environment:
      - COLLECTOR_SLEEP_DURATION=30
      - COLLECTOR_MEASUREMENT_FREQUENCY=600
```
