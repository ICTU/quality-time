# Deployment instructions

This document describes how to deploy, and if needed move, the *Quality-time* application. It is aimed at *Quality-time* operators.

*Quality-time* consists of a set of Docker containers that together form the application. See the [software documentation](software.md) for an overview of the different containers. It is assumed the containers are deployed using a docker-composition.

*Quality-time* furthermore assumes an LDAP service is available to authenticate users or that forwarded authentication is used.

## Docker-composition

This document assumes docker-compose is used to deploy the containers. The [docker folder](https://github.com/ICTU/quality-time/tree/master/docker) of the *Quality-time* repository contains different compose files for running *Quality-time* in development and continuous integration mode. You can use these compose files as basis for your own deployment configuration.

## Configuring authentication (mandatory)

You need to either configure an LDAP server to authenticate users with or configure forwarded authentication.

### LDAP

To configure an LDAP server to authenticate users with, set the `LDAP_URL`, `LDAP_ROOT_DN`, `LDAP_LOOKUP_USER_DN`, `LDAP_LOOKUP_USER_PASSWORD`, and `LDAP_SEARCH_FILTER` environment variables.
Note that `LDAP_URL` may be a comma-separated list of LDAP connection URL(s).
Add the LDAP environment variables to the external server service in the [compose file](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml):

```yaml
  external_server:
    environment:
      - LDAP_URL=ldap://ldap:389
      - LDAP_ROOT_DN=dc=example,dc=org
      - LDAP_LOOKUP_USER_DN=cn=admin,dc=example,dc=org
      - LDAP_LOOKUP_USER_PASSWORD=admin
      - LDAP_SEARCH_FILTER=(|(uid=$username)(cn=$username))
```

When using the `LDAP_SEARCH_FILTER` as shown above, users can use either their LDAP canonical name (`cn`) or their LDAP user id to login. The `$username` variable is filled by *Quality-time* at run time with the username that the user enters in the login dialog box.

```{seealso}
See [https://ldap.com/ldap-filters/](https://ldap.com/ldap-filters/) for more information on LDAP filters.
```

```{index} Forwarded Authentication
```

### Forwarded authentication

To configure Forwarded Authentication, set the `FORWARD_AUTH_ENABLED` and `FORWARD_AUTH_HEADER` environment variables. Add the environment variables to the external server service in the [compose file](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml):

```yaml
  external_server:
    environment:
      - FORWARD_AUTH_ENABLED=True
      - FORWARD_AUTH_HEADER=X-Forwarded-User
```

```{danger}
Only enable Forwarded Authentication if *Quality-time* is setup behind a reverse proxy that is responsible for authentication and direct access to *Quality-time* is not possible.
```

## Configuring hostnames and ports (optional)

The hostnames and ports of the different containers can be configured via environment variables. See the [software documentation](software.md) for an overview of the available hostname and port environment variables per component.

## Configuring example reports (optional)

By default, the server components will check for the presence of example reports in the database on startup. If none are present, three example reports will be added to the database. To prevent this behavior, set the `LOAD_EXAMPLE_REPORTS` environment variable to false for both the external and the internal server:

```yaml
  external_server:
    environment:
      - LOAD_EXAMPLE_REPORTS=False
  internal_server:
    environment:
      - LOAD_EXAMPLE_REPORTS=False
```

## Configuring measurement frequency (optional)

The collector component is responsible for collecting measurement data from sources. It wakes up periodically and asks the internal server for a list of all metrics. For each metric, the collector gets the measurement data from each of its sources and posts a new measurement to the internal server.

If a metric has been recently measured and its parameters haven't been changed, the collector skips the metric.

By default, the collector measures metrics whose configuration hasn't been changed every 15 minutes, sleeps 60 seconds in between measurements, and measures at most 30 metrics every time it wakes up. The defaults can be changed as follows:

```yaml
  collector:
    environment:
      - COLLECTOR_SLEEP_DURATION=10  # Wake up every 10 seconds
      - COLLECTOR_MEASUREMENT_LIMIT=25  # Measure at most 25 metrics on every wake up
      - COLLECTOR_MEASUREMENT_FREQUENCY=600  # Measure metrics at least every 10 minutes
```

```{warning}
Note that the frontend warns users when metrics have not been measured for a long period, currently hardcoded to one hour. That means that if you set the collector measurement frequency to more than one hour, users will see warnings that the measurement data is old.
```

## Configuring notification frequency (optional)

The notifier component is responsible for notifying users via MS Teams about changed metric statuses. It wakes up periodically and asks the internal server fo a list of all metrics. For each metric, the notifier decides whether a notification is possible and needed.

By default, the notifier wakes up every minute to check for changed metric statuses. This frequency can be changed as follows:

```yaml
  notifier:
    environment:
      - NOTIFIER_SLEEP_DURATION=120  # Check for notifications every two minutes
```

## Configuring MongoDB credentials (optional)

The default MongoDB credentials can be changed as follows:

```yaml
  database:
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secret
```

See the [documentation on the MongoDB image](https://hub.docker.com/_/mongo) for more information.

## Configuring renderer localisation (optional)

The date/time format and timezone of the reports that user sees are determined by the user's browser. To configure the date/time format and timezone of exported PDFs, the renderer can be configured as follows:

```yaml
  renderer:
    environment:
      - LC_ALL=en_GB.UTF-8  # To get European dates (DD-MM-YYYY)
      - TZ=Europe/Amsterdam  # To get Central European Time
```

## Moving *Quality-time*

The easiest way to move a *Quality-time* instance is to deploy a new *Quality-time* instance at the new location and then copy the database contents from the old instance to the new instance. All *Quality-time* data is contained in the Mongo database, so that is the only data that needs to be copied.

Start a new mongo container and use that to run the `mongodump` and `mongorestore` commands:

```console
docker run -dP --rm --name mongo mongo
docker exec -ti mongo mongodump --uri "mongodb://root:<pwd>@<hostname or ip>:27017" --out /tmp/dump/qt_dump
docker exec -ti mongo mongorestore --uri "mongodb://root:<pwd>@<hostname or ip>:27017" /tmp/dump/qt_dump
```

The `<hostname or ip>` is the hostname or IP address of the Swarm manager in case of Docker Swarm.

As the dump is stored in a temporary container, the dump will disappear as soon as the container is removed. To keep the dump around, map a folder (`-v`) in the `mongo` container.

```{seealso}
See [Back Up and Restore with MongoDB Tools](https://docs.mongodb.com/docs/manual/tutorial/backup-and-restore-tools/) for more information about the `mongodump` and `mongorestore` commands.
```
