# Deployment instructions

Quality-time consists of a set of containers that together form the application: a proxy that routes incoming traffic to either the frontend container to serve the React frontend and static resources or to the server container that serves the REST API. The database container runs a Mongo database server. The renderer containers is responsible for converting reports to PDF. The collector container collects the measurement data for the metrics. Finally, the notifier container notifies users of significant events, like metrics turning red.

In addition, *Quality-time* assumes an LDAP service is available to authenticate users or that forwarded authentication is used.

## Docker-composition

This document assumes docker-compose is used to deploy the containers. The [docker folder](https://github.com/ICTU/quality-time/tree/master/docker) of the *Quality-time* repo contains different compose files for running *Quality-time* in development and continuous integration mode. You can use these compose files as basis for your own deployment configuration.

## Configuring LDAP

To configure an LDAP server to authenticate users with, set the `LDAP_URL`, `LDAP_ROOT_DN`, `LDAP_LOOKUP_USER_DN`, `LDAP_LOOKUP_USER_PASSWORD`, and `LDAP_SEARCH_FILTER` environment variables. Add the LDAP environment variables to the server service in the [compose file](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml):

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

```{index} Forwarded Authentication
```

## Configuring Forwarded Authentication

To configure Forwarded Authentication, set the `FORWARD_AUTH_ENABLED` and `FORWARD_AUTH_HEADER` environment variables. Security warning: Only enable Forwarded Authentication if *Quality-time* is setup behind a reverse proxy that is responsible for authentication and direct access to *Quality-time* is not possible. Add the environment variables to the server service in the [compose file](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml):

```yaml
  server:
    environment:
      - FORWARD_AUTH_ENABLED=True
      - FORWARD_AUTH_HEADER=X-Forwarded-User
```

## Settings per component

### Proxy

External traffic is routed by a {index}`Caddy` reverse proxy (container name: www) to either the frontend container or the server container. The proxy listens on port 80. You can override the Caddy configuration in the [compose file](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml) if so desired.

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

The {index}`API` is accessible at the server container, running at port 5001 by default. The Caddy reverse proxy routes URLs that start with /api to the server. To configure the server container port, set the `SERVER_PORT` environment variable. Add the `SERVER_PORT` environment variable to the server, the collector, and the notifier services:

```yaml
  server:
    environment:
      - SERVER_PORT=6001
  collector:
    environment:
      - SERVER_PORT=6001
  notifier:
    environment:
      - SERVER_PORT=6001
```

### Collector

The collector contacts the server to see whether there are metrics that need to be measured and uses the server API to store the new measurements in the database. By default, the collector measures metrics whose configuration hasn't been changed every 15 minutes and sleeps 60 seconds in between measurements.

To configure the sleep duration and the measurement frequency, set the `COLLECTOR_SLEEP_DURATION` and `COLLECTOR_MEASUREMENT_FREQUENCY` environment variables. Both variables have seconds as unit. Add the `COLLECTOR_SLEEP_DURATION` and `COLLECTOR_MEASUREMENT_FREQUENCY` environment variables to the collector service:

```yaml
  collector:
    environment:
      - COLLECTOR_SLEEP_DURATION=30
      - COLLECTOR_MEASUREMENT_FREQUENCY=600
```

To optionally configure a proxy for the collector to use, set the `HTTP_PROXY` or `HTTPS_PROXY` environment variable, for example:

```yaml
  collector:
    environment:
      - HTTP_PROXY="http://proxy.com"
```

See the [aiohttp documentation](https://docs.aiohttp.org/en/stable/client_advanced.html#proxy-support) for more information on proxy support.

### Notifier

The notifier is responsible for notifying users about significant events, such as metrics turning red. It wakes up periodically and asks the server for all reports. For each report, the notifier determines whether whether notification destinations have been configured, and whether events happened that users need to be notified of.

To configure the sleep duration, set the `NOTIFIER_SLEEP_DURATION` environment variable. The variable has seconds as unit. Add the `NOTIFIER_SLEEP_DURATION` environment variable to the notifier service:

```yaml
  notifier:
    environment:
      - NOTIFIER_SLEEP_DURATION=60
```

### Renderer

The renderer converts *Quality-time* reports into PDFs. Currently, https has not been configured for communication between containers, so `ALLOW_HTTP` needs to be true.

The renderer can be localized by setting the `LC_ALL` (locale) and `TZ` (timezone) environment variables, for example:

```yaml
  renderer:
    environment:
      - ALLOW_HTTP=true
      - LC_ALL=en_GB.UTF-8  # Set the date format in the PDF export to DD-MM-YYYY
      - TZ=Europe/Amsterdam  # Set the timezone to CET
```
