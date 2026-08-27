# Deployment instructions

This document describes how to deploy, and if needed move, the *Quality-time* application. It is aimed at *Quality-time* operators.

*Quality-time* consists of a set of Docker containers that together form the application.
See the [software documentation](software.md) for an overview of the different containers.
It is assumed the containers are deployed using a Docker-composition.

*Quality-time* furthermore assumes an LDAP service is available to authenticate users or that forwarded authentication is used.

```{warning}
Before skipping versions or downgrading, see the [version policy](versioning.md).
```

## Docker-composition

This document assumes Docker is used to deploy the containers. The [docker folder](https://github.com/ICTU/quality-time/tree/master/docker) of the *Quality-time* repository contains different compose files for running *Quality-time* in development and continuous integration mode. You can use these compose files as basis for your own deployment configuration.

```{note}
Per the [version policy](versioning.md), if the Docker-composition needs changes, this will be indicated by a new major release of *Quality-time*.
```

To deploy *Quality-time* locally, follow these steps:

1. Make a directory, e.g. `quality_time` and change directory to it.
2. Download the docker compose files from the [docker folder](https://github.com/ICTU/quality-time/tree/master/docker) and place them in the folder created in the previous step.
3. Set the version number: `export QUALITY_TIME_VERSION=v5.0.0`.
4. Run `docker compose up`.
5. Go to [http://localhost](http://localhost) to access the application.
6. To log in, use one of the default users available in the [test LDAP server](software.md#test-ldap-server).

Internally, the application listens on port 80 by default.
To change this, set the `PROXY_PORT` environment variable to a different port before starting the application.
For example: `export PROXY_PORT=8080`.
Externally, the application listens on port 80 by default.
To changes this, adapt the default port mapping of the `www` service in the compose file.
For example:

```yaml
services:
  www:
    ports:
      - "1080:${PROXY_PORT:-80}"
```

## Kubernetes

The helm chart for deploying on Kubernetes is deployed to [Docker Hub](https://hub.docker.com/r/ictu/quality-time/tags). The chart version is coupled to the Quality-time version and updated on every release of Quality-time. A sample `values.yaml` can be found in the [helm folder](https://github.com/ICTU/quality-time/tree/master/helm).

Note that the helm chart does not support overriding port numbers.
Although setting port environment variables in the `values.yaml` will change the ports that the app within the pod listens to, it will *not* change the service port mapping and therefore lead to a malfunctioning service.
Instead, only the ingress should be configured.

## Configuring authentication (mandatory)

You need to either configure an LDAP server to authenticate users with or configure forwarded authentication.

### LDAP

To configure an LDAP server to authenticate users with, set the `LDAP_URL`, `LDAP_ROOT_DN`, `LDAP_LOOKUP_USER_DN`, `LDAP_LOOKUP_USER_PASSWORD`, and `LDAP_SEARCH_FILTER` environment variables.
Note that `LDAP_URL` may be a comma-separated list of LDAP connection URL(s).

Add the LDAP environment variables to the API-server service in the [compose file](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml):

```yaml
services:
  api_server:
    environment:
      - LDAP_URL=ldap://ldap:389
      - LDAP_ROOT_DN=dc=example,dc=org
      - LDAP_LOOKUP_USER_DN=cn=admin,dc=example,dc=org
      - LDAP_LOOKUP_USER_PASSWORD=admin
      - LDAP_SEARCH_FILTER=(|(uid=$username)(cn=$username))
```

Because environment variables can be read by anyone with access to the Docker daemon, [it is recommended to store secrets in files](https://docs.docker.com/compose/how-tos/use-secrets/). Set `LDAP_LOOKUP_USER_PASSWORD_FILE` to the name of a file containing the password of the LDAP lookup user, instead of setting `LDAP_LOOKUP_USER_PASSWORD`. This is how the compose file that comes with *Quality-time* is configured:

```yaml
services:
  api_server:
    environment:
      - LDAP_LOOKUP_USER_PASSWORD_FILE=/run/secrets/ldap_lookup_user_password
    secrets:
      - ldap_lookup_user_password
secrets:
  ldap_lookup_user_password:
    file: ldap_lookup_user_password.txt
```

Change the contents of the `ldap_lookup_user_password.txt` file to the password of your LDAP lookup user, or point the secret to a file of your own. If both `LDAP_LOOKUP_USER_PASSWORD_FILE` and `LDAP_LOOKUP_USER_PASSWORD` are set, the file takes precedence.

Alternatively, for a Kubernetes deployment, add the LDAP environment variables to the API-server service in the [Helm values.yaml](https://github.com/ICTU/quality-time/blob/master/helm/values.yaml):

```yaml
services:
  api_server:
    env:
      LDAP_URL: "ldap://host.docker.internal:389"
      LDAP_ROOT_DN: "dc=example,dc=org"
      LDAP_LOOKUP_USER_DN: "cn=admin,dc=example,dc=org"
      LDAP_LOOKUP_USER_PASSWORD: "admin"
      LDAP_SEARCH_FILTER: "(|(uid=$$username)(cn=$$username))"
```

When using the `LDAP_SEARCH_FILTER` as shown above, users can use either their LDAP canonical name (`cn`) or their LDAP user id to login. The `$username` variable is filled by *Quality-time* at run time with the username that the user enters in the login dialog box.

```{seealso}
See [https://ldap.com/ldap-filters/](https://ldap.com/ldap-filters/) for more information on LDAP filters.
```

Quality-time tries two methods to authenticate users:

- If the LDAP-server returns the `userPassword` (containing a hash of the users' password), Quality-time uses that to verify the password. Note that currently only `ARGON2` hashes are supported. Please submit a feature request if you need support for another type of hash.
- If the `userPassword` is not returned or it is no `ARGON2` hash, Quality-time attempts an LDAP-bind operation using the user's distinguished name as returned by the LDAP-server and the password entered by the user.

```{index} Forwarded Authentication
```

### Forwarded authentication

To configure Forwarded Authentication, set the `FORWARD_AUTH_ENABLED` and `FORWARD_AUTH_HEADER` environment variables. Add the environment variables to the API-server service in the [compose file](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml):

```yaml
services:
  api_server:
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

By default, the server will check for the presence of example reports in the database on startup. If none are present, three example reports will be added to the database. To prevent this behavior, set the `LOAD_EXAMPLE_REPORTS` environment variable to false for the API-server:

```yaml
services:
  api_server:
    environment:
      - LOAD_EXAMPLE_REPORTS=False
```

## Configuring user session duration (optional)

By default, the server will log out logged-in users after 120 hours. To change the default user session duration, set the `USER_SESSION_DURATION` environment variable to the desired session duration (in hours):

```yaml
services:
  api_server:
    environment:
      - USER_SESSION_DURATION=48
```

## Configuring measurement frequency (optional)

The collector component is responsible for collecting measurement data from sources. It wakes up periodically and gets a list of all metrics from the database. For each metric, the collector gets the measurement data from each of its sources and stores a new measurement in the database.

If a metric has been recently measured and its parameters haven't been changed, the collector skips the metric.

By default, the collector measures metrics whose configuration hasn't been changed every 15 minutes, sleeps 20 seconds in between measurements, measures at most 30 metrics every time it wakes up, and times out connections to sources after 2 minutes. The defaults can be changed as follows:

```yaml
services:
  collector:
    environment:
      - COLLECTOR_SLEEP_DURATION=10  # Wake up every 10 seconds
      - COLLECTOR_MEASUREMENT_FREQUENCY=600  # Measure metrics at least every 10 minutes
      - COLLECTOR_MEASUREMENT_LIMIT=25  # Measure at most 25 metrics on every wake up
      - COLLECTOR_MEASUREMENT_TIMEOUT=180  # Timeout connections to sources after 3 minutes
```

```{warning}
Note that the frontend warns users when metrics have not been measured for a long period, currently hardcoded to one hour. That means that if you set the collector measurement frequency to more than one hour, users will see warnings that the measurement data is old.
```

## Configuring notification frequency (optional)

The notifier component is responsible for notifying users via MS Teams about changed metric statuses. It wakes up periodically and gets a list of all metrics from the database. For each metric, the notifier decides whether a notification is possible and needed.

By default, the notifier wakes up every minute to check for changed metric statuses. This frequency can be changed as follows:

```yaml
services:
  notifier:
    environment:
      - NOTIFIER_SLEEP_DURATION=120  # Check for notifications every two minutes
```

## Configuring MongoDB credentials (optional)

The default {index}`MongoDB` credentials can be changed as follows:

```yaml
services:
  database:
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=secret
```

In production, [it is recommended to store secrets in files](https://docs.docker.com/compose/how-tos/use-secrets/):

```yaml
services:
  database:
    environment:
      - MONGO_INITDB_ROOT_USERNAME_FILE=/run/secrets/database_username
      - MONGO_INITDB_ROOT_PASSWORD_FILE=/run/secrets/database_password
    secrets:
      - database_username
      - database_password
secrets:
  database_password:
    file: database_password.txt
  database_username:
    file: database_username.txt
```

See the [documentation on the MongoDB image](https://hub.docker.com/_/mongo) for more information.

## Configuring renderer localisation (optional)

The date/time format and timezone of the reports that a user sees are determined by the user's browser. To configure the date/time format and timezone of exported PDFs, the renderer can be configured as follows:

```yaml
  renderer:
    environment:
      - LC_ALL=en_GB.UTF-8  # To get European dates (DD-MM-YYYY)
      - TZ=Europe/Amsterdam  # To get Central European Time
```

## Configuring renderer proxy (optional)

```yaml
  renderer:
    environment:
      - PROXY_HOST=www  # Hostname of service
      - PROXY_PORT=80  # Port of service
      - PROXY_PROTOCOL=http  # http/https
```

## Configuring logging (optional)

The options for configuring logging are limited at the moment. The MongoDB daemon can be told to produce less logging by passing the `--quiet` flag:

```yaml
  database:
    command: --quiet
```

The collector, notifier, and API-server all have log level `WARNING` as default. This can be overridden by setting an environment variable to `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`.

| Component  | Log level environment variable |
|:-----------|:-------------------------------|
| Collector  | `COLLECTOR_LOG_LEVEL`          |
| API-server | `API_SERVER_LOG_LEVEL`         |
| Notifier   | `NOTIFIER_LOG_LEVEL`           |

The proxy access log is turned off. Please submit an issue if you need this and possibly other logging settings to be configurable.

## Moving *Quality-time*

The easiest way to move a *Quality-time* instance is to deploy a new *Quality-time* instance at the new location and then copy the database contents from the old instance to the new instance. All *Quality-time* data is contained in the Mongo database, so that is the only data that needs to be copied. The same procedure can be used to back up a *Quality-time* instance and restore it later.

Copying the database is done with the MongoDB Database Tools `mongodump` and `mongorestore`. The *Quality-time* database container image does not contain these tools, so run them from a separate container, based on the [official MongoDB image](https://hub.docker.com/_/mongo), or [install them locally](https://www.mongodb.com/docs/database-tools/installation/installation/). Use the same major MongoDB version as the *Quality-time* database container. To look up that version, see the `FROM` instruction in the [Dockerfile of the database component](https://github.com/ICTU/quality-time/blob/master/components/database/Dockerfile).

The database does not publish a port. Run the tools in the same network as the database, or forward the database port to the machine where the tools run, as described per deployment type below.

In the commands below, replace `<username>` and `<password>` with the [MongoDB credentials](#configuring-mongodb-credentials-optional) of the instance being addressed. The source and the target instance can have different credentials. Pass the options as shown:

- `authSource=admin`, because the MongoDB credentials are those of the administrator, which MongoDB stores in the `admin` database.
- `--drop`, so that `mongorestore` empties each collection before restoring it. A freshly deployed *Quality-time* instance creates collections, and optionally [example reports](#configuring-example-reports-optional), when it starts, which would otherwise be mixed with the restored data.

### Docker-composition

Docker compose puts the containers in a network named after the compose project, `<compose project>_default`, where the compose project defaults to the name of the folder that contains the compose file. Use `docker network ls` to look up the exact name.

Run `mongodump` in a temporary container in the network of the old instance, and write the dump to a file on the host:

```console
docker run --rm --network <compose project>_default mongo:<major version> \
    mongodump --uri "mongodb://<username>:<password>@database:27017/quality_time_db?authSource=admin" \
    --archive --quiet > qt_dump.archive
```

Run `mongorestore` in a temporary container in the network of the new instance, and read the dump from the file on the host:

```console
docker run --rm --interactive --network <compose project>_default mongo:<major version> \
    mongorestore --uri "mongodb://<username>:<password>@database:27017/?authSource=admin" \
    --archive --drop < qt_dump.archive
```

The old and the new instance each have their own network, also when they run on the same machine, so make sure to use the compose project name of the old instance when dumping and that of the new instance when restoring.

### Kubernetes

Forward the port of the database service to the machine where the MongoDB Database Tools are installed:

```console
kubectl port-forward service/<release name>-database 27017:27017
```

Then, in another terminal, dump the database of the old instance:

```console
mongodump --uri "mongodb://<username>:<password>@localhost:27017/quality_time_db?authSource=admin" \
    --archive=qt_dump.archive
```

Stop the port forward, start a port forward to the new instance, and restore the dump:

```console
mongorestore --uri "mongodb://<username>:<password>@localhost:27017/?authSource=admin" \
    --archive=qt_dump.archive --drop
```

Alternatively, if the MongoDB Database Tools cannot be installed locally, run them in a temporary pod in the same namespace as the *Quality-time* instance. Run the `mongodump` command in the namespace of the old instance and the `mongorestore` command in the namespace of the new instance, creating a temporary pod in each:

```console
kubectl run mongo-tools --image=mongo:<major version> --restart=Never --command -- sleep 3600
kubectl exec mongo-tools -- \
    mongodump --uri "mongodb://<username>:<password>@<release name>-database:27017/quality_time_db?authSource=admin" \
    --archive --quiet > qt_dump.archive
kubectl exec --stdin mongo-tools -- \
    mongorestore --uri "mongodb://<username>:<password>@<release name>-database:27017/?authSource=admin" \
    --archive --drop < qt_dump.archive
kubectl delete pod mongo-tools
```

```{seealso}
See [Back Up and Restore a Self-Managed Deployment with MongoDB Tools](https://www.mongodb.com/docs/manual/tutorial/backup-and-restore-tools/) for more information about the `mongodump` and `mongorestore` commands. Both commands accept a `--gzip` option to compress the archive. Pass it to both commands or to neither.
```
