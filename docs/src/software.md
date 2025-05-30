# Software documentation

This document describes the *Quality-time* software. It is aimed at *Quality-time* developers and maintainers.

## Component overview

```{eval-rst}
.. graphviz:: components-dark.dot
   :class: only-dark

.. graphviz:: components-light.dot
   :class: only-light
```

*Quality-time* consists of seven Docker components, as depicted above. Each oval is a Docker component.

### Bespoke components

There are four bespoke components:

- A [frontend](#frontend), serving the user interface. The frontend is written in JavaScript using [ReactJS](https://reactjs.org) and [Material UI](https://mui.com).
- An [API-server](#api-server) serving the API for the user interface. The API-server is written in Python using [Bottle](https://bottlepy.org) as web framework.
- A [collector](#collector) to collect the measurements from the sources. The collector is written in Python using [`aiohttp`](https://docs.aiohttp.org) as HTTP client library.
- A [notifier](#notifier) to notify users about events such as metrics turning red. The notifier is written in Python.

Source code that is shared between the Python components lives in the [shared data model](#shared-data-model) and [shared code](#shared-code) components. These are not run-time components. The code of these components is shared at build time, when the Docker images are created. The data model and shared code are used by all Python components, i.e. the API-server, the collector, and the notifier.

### Standard components

*Quality-time* uses three standard components:

- A [proxy](#proxy), routing traffic from and to the user's browser. The proxy is based on [Nginx](https://nginx.org).
- A [database](#database), for storing reports and measurements. The database is based on [MongoDB](https://www.mongodb.com).
- A [renderer](#renderer), to export reports to PDF. The renderer is based on [Puppeteer](https://pptr.dev).

In addition, unless forward authentication is used, an LDAP server is expected to be available to authenticate users.

### Test components

For testing purposes there a few additional components:

- A web server serving [test data](#test-data).
- A [test LDAP server](#test-ldap-server).
- A tool to administer users in the LDAP server (phpldapadmin).
- A tool to view and edit the database contents (mongo-express).

## Frontend

The frontend contains the React frontend code.

### Health check

As a health check, the favicon is downloaded.

### Environment variables

The frontend uses the following environment variables:

| Name            | Default value | Description                       |
|:----------------|:--------------|:----------------------------------|
| `FRONTEND_PORT` | `5000`        | The port the frontend listens on. |

## API-server

```{index} API
```

### API

The API of the API-server is versioned. The version is not changed when backwards compatible changes are made, such as the addition of new endpoints. The public [API](api.md) is documented separately.

### Health check

The [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/api_server/Dockerfile) contains a health check script that downloads the health information from the API-server end-point `/api/internal/health`.

If the server is healthy the end-point returns a response with HTTP-status 200 and a JSON payload containing:

```json
{
    "healthy": true
}
```

### Environment variables

The API-server uses the following environment variables:

| Name                        | Default value                             | Description                                                                                                                                                                                                                                                                 |
|:----------------------------|:------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `API_SERVER_PORT`           | `5001`                                    | Port of the API-server.                                                                                                                                                                                                                                                     |
| `API_SERVER_LOG_LEVEL`      | `WARNING`                                 | Log level. Allowed values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.                                                                                                                                                                                          |
| `DATABASE_URL`              | `mongodb://root:root@localhost:27017`     | Mongo database connection URL.                                                                                                                                                                                                                                              |
| `DATABASE_USERNAME`         | `root`                                    | Mongo database connection username. This value is only used when `DATABASE_URL` is not provided.                                                                                                                                                                            |
| `DATABASE_PASSWORD`         | `root`                                    | Mongo database connection password. This value is only used when `DATABASE_URL` is not provided.                                                                                                                                                                            |
| `DATABASE_HOST`             | `localhost`                               | Mongo database connection hostname. This value is only used when `DATABASE_URL` is not provided.                                                                                                                                                                            |
| `DATABASE_PORT`             | `27017`                                   | Mongo database connection port. This value is only used when `DATABASE_URL` is not provided.                                                                                                                                                                                |
| `LDAP_URL`                  | `ldap://ldap:389`                         | Comma-separated list of LDAP connection URL(s).                                                                                                                                                                                                                             |
| `LDAP_ROOT_DN`              | `dc=example,dc=org`                       | LDAP root distinguished name.                                                                                                                                                                                                                                               |
| `LDAP_LOOKUP_USER_DN`       | `cn=admin,dc=example,dc=org`              | LDAP lookup user distinguished name.                                                                                                                                                                                                                                        |
| `LDAP_LOOKUP_USER_PASSWORD` | `admin`                                   | LDAP lookup user password.                                                                                                                                                                                                                                                  |
| `LDAP_SEARCH_FILTER`        | `(&#124;(uid=$$username)(cn=$$username))` | LDAP search filter. With this default search filter, users can use either their LDAP canonical name (`cn`) or their LDAP user id to login. The `$username` variable is filled by *Quality-time* at run time with the username that the user enters in the login dialog box. |
| `LOAD_EXAMPLE_REPORTS`      | `True`                                    | Whether or not to import example reports in the database on start up.                                                                                                                                                                                                       |
| `FORWARD_AUTH_ENABLED`      | `False`                                   | Whether or not to enable forward authentication.                                                                                                                                                                                                                            |
| `FORWARD_AUTH_HEADER`       | `X-Forwarded-User`                        | Header to use for getting the username if forward authentication is turned on.                                                                                                                                                                                              |
| `USER_SESSION_DURATION`     | `120`                                     | Duration of user session in number of hours.                                                                                                                                                                                                                                |

## Collector

The collector is responsible for collecting measurement data from sources. It wakes up periodically and retrieves a list of all metrics from the database. For each metric, the collector gets the measurement data from each of its sources and stores a new measurement to the database.

If a metric has been recently measured and its parameters haven't been changed, the collector skips the metric.

By default, the collector measures metrics whose configuration hasn't been changed every 15 minutes and sleeps 60 seconds in between measurements. This can be changed using the environment variables listed below.

### Health check

Every time the collector wakes up, it writes the current date and time in ISO format to the health check file. This date and time is read by the Docker health check (see the [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/collector/Dockerfile)). If the written date and time are too long ago, the collector container is considered to be unhealthy.

### Environment variables

The collector uses the following environment variables:

| Name                              | Default value                         | Description                                                                                                                                                                       |
|:----------------------------------|:--------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `COLLECTOR_LOG_LEVEL`             | `WARNING`                             | Log level. Allowed values are `DEBUG`, `INFO`, `WARNING`, `CRITICAL`, and `ERROR`.                                                                                                |
| `COLLECTOR_SLEEP_DURATION`        | `20`                                  | The maximum amount of time (in seconds) that the collector sleeps between collecting measurements.                                                                                |
| `COLLECTOR_MEASUREMENT_FREQUENCY` | `900`                                 | The amount of time (in seconds) after which a metric should be measured again.                                                                                                    |
| `COLLECTOR_MEASUREMENT_LIMIT`     | `30`                                  | The maximum number of metrics that the collector measures each time it wakes up. If more metrics need to be measured, they will be measured the next time the collector wakes up. |
| `COLLECTOR_MEASUREMENT_TIMEOUT`   | `120`                                 | The amount of time (in seconds) after which a source connection should timeout.                                                                                                   |
| `DATABASE_URL`                    | `mongodb://root:root@localhost:27017` | Mongo database connection URL.                                                                                                                                                    |
| `DATABASE_USERNAME`               | `root`                                | Mongo database connection username. This value is only used when `DATABASE_URL` is not provided.                                                                                  |
| `DATABASE_PASSWORD`               | `root`                                | Mongo database connection password. This value is only used when `DATABASE_URL` is not provided.                                                                                  |
| `DATABASE_HOST`                   | `localhost`                           | Mongo database connection hostname. This value is only used when `DATABASE_URL` is not provided.                                                                                  |
| `DATABASE_PORT`                   | `27017`                               | Mongo database connection port. This value is only used when `DATABASE_URL` is not provided.                                                                                      |
| `HEALTH_CHECK_FILE`               | `/home/collector/health_check.txt`    | Path to the file used for health check.                                                                                                                                           |
| `HTTP(S)_PROXY`                   |                                       | Proxy to use by the collector.                                                                                                                                                    |

```{seealso}
See the [`aiohttp` documentation](https://docs.aiohttp.org/en/stable/client_advanced.html#proxy-support) for more information on proxy support.
```

## Notifier

The notifier is responsible for notifying users about significant events, such as metrics turning red. It wakes up periodically and asks the server for all reports. For each report, the notifier determines whether notification destinations have been configured, and whether events happened that need to be notified.

### Health check

Every time the notifier wakes up, it writes the current date and time in ISO format to the health check file. This date and time is read by the Docker health check (see the [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/notifier/Dockerfile)). If the written date and time are too long ago, the notifier container is considered to be unhealthy.

### Environment variables

The notifier uses the following environment variables:

| Name                      | Default value                         | Description                                                                                      |
|:--------------------------|:--------------------------------------|:-------------------------------------------------------------------------------------------------|
| `DATABASE_URL`            | `mongodb://root:root@localhost:27017` | Mongo database connection URL.                                                                   |
| `DATABASE_USERNAME`       | `root`                                | Mongo database connection username. This value is only used when `DATABASE_URL` is not provided. |
| `DATABASE_PASSWORD`       | `root`                                | Mongo database connection password. This value is only used when `DATABASE_URL` is not provided. |
| `DATABASE_HOST`           | `localhost`                           | Mongo database connection hostname. This value is only used when `DATABASE_URL` is not provided. |
| `DATABASE_PORT`           | `27017`                               | Mongo database connection port. This value is only used when `DATABASE_URL` is not provided.     |
| `HEALTH_CHECK_FILE`       | `/home/notifier/health_check.txt`     | Path to the file used for health check.                                                          |
| `NOTIFIER_LOG_LEVEL`      | `WARNING`                             | Log level. Allowed values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.               |
| `NOTIFIER_SLEEP_DURATION` | `60`                                  | The amount of time (in seconds) that the notifier sleeps between sending notifications.          |

## Shared code

The [shared code component](https://github.com/ICTU/quality-time/tree/master/components/shared_code) contains code and resources shared between the API-server, the collector, and the notifier. This includes the [example reports](#example-reports), a [shared data model](#shared-data-model), and code to initialize the servers, access the database, and provide endpoints.

### Example reports

The [example reports](https://github.com/ICTU/quality-time/tree/master/components/shared_code/src/shared/example-reports) are imported when a server is started and the database doesn't contain any sample reports yet. Turn off the loading of example report by setting `LOAD_EXAMPLE_REPORTS` to `False`. See the sections on configuration of the servers below.

## Shared data model

The [shared data model](https://github.com/ICTU/quality-time/tree/master/components/shared_code/src/shared_data_model) contains the data model that is shared between all Python components.

### Data model

The data model package describes the domain model used by the application. It allows for a frontend that doesn't need to know about specific metrics and sources. When a server component starts up, it checks whether the data model has changed, and if so, imports it into the database.

The data model package consists of a meta model and the data model itself. The data model consists of four major parts:

- Scales
- Metrics
- Sources
- Subjects

The meta model uses Pydantic to specify the components and attributes of the data model.

#### Scales

The `scales` part of the data model defines the scales that can be used to measure metrics. At the time of writing these include an absolute count scale, a percentage scale, and a version number scale.

Each metric defines the scales it supports.

#### Metrics

The `metrics` part of the data model is a dictionary with all supported metric types. The keys are the metric type names. The values are objects describing the metric type. All metric types have the following meta model:

```python
class Metric(DescribedModel):
    """Base model for metrics."""

    scales: list[str] = Field(["count"], min_length=1)
    default_scale: str = "count"
    unit: Unit = Unit.NONE
    addition: Addition = Addition.SUM
    direction: Direction = Direction.FEWER_IS_BETTER
    target: str = "0"
    near_target: str = "10"
    evaluate_targets: bool = True
    sources: list[str] = Field(..., min_items=1)
    tags: list[Tag] = []
    rationale: str = ""  # Answers the question "Why measure this metric?", included in documentation and UI
    rationale_urls: list[str] = []
    explanation: str | None = ""  # Optional explanation of concepts in text format, included in documentation and UI
    explanation_urls: list[str] = []
    documentation: str | None = ""  # Optional documentation in Markdown format, only included in the documentation
```

The `name` is the default name of metrics of this type. The `description` describes what the metric measures. These are part of the `DescribedModel`.

The `scales` list shows which scales the metric supports and the `default_scale` specifies which scale is the default scale.

The `unit` is the default unit of the metric, e.g. lines of code, security warnings, or in the above example, complex units.

The `addition` determines how values from multiple sources are combined: possible values are `max`, `min`, and `sum`.

The `direction` specifies whether smaller measurement values are better or worse.

The `target` is the default target value for the metric. The `near_target` is when the metric becomes red. Values between `target` and `near_target` are yellow.

The `evaluate_targets` flag determines whether the metric is "Informative" or not. If `evaluate_targets` is `True`, the measurement values are compared to the `target` and `near_target` and the metric status depends on the result of the comparison. If `evaluate_targets` is `False`, the metric status is "Informative" regardless of the measurement value. Unless there are no measurements, in which case the status is "Unknown". Note that the user can change any metric from being evaluated to informative and vice versa, so all metrics should have a `target` and `near_target` value.

The list of `sources` contains the keys of source types that support this metric type.

Finally, `tags` are strings used to group related metrics.

Users with sufficient rights can override the default name, unit, and target of metrics via the user interface.

#### Sources

The `sources` part of the data model is a dictionary that describes all supported source types. The keys are the source type names. The values are objects describing the source type. All source types have the following meta model:

```python
class Source(DescribedModel):
    """The source model extends the base model with source parameters and measurement entities."""

    url: HttpsUrl | None = None
    documentation: dict[str, str] | None = None  # Documentation in Markdown format
    configuration: dict[str, Configuration] = {}
    parameters: dict[str, Parameter]
    entities: dict[str, Entity] = {}
    issue_tracker: bool | None = False
```

The `name` is the default name of sources of this type. The `description` gives some background information on the source type. These are part of the `DescribedModel`.

The `url` links to a landing page describing the source type.

##### Configuration

In cases where *Quality-time* needs information about sources that doesn't need to be parameterizable, `Configurations` can be added to the source. A configuration consists of a name (via `NamedModel`), a list of metrics to which the configuration applies, and a value:

```python
class Configuration(NamedModel):
    """Configuration for specific metrics."""

    metrics: list[str] = Field(..., min_items=1)
    value: list[str] = Field(..., min_items=1)
```

##### Parameters

The `parameters` describe the parameters that need to be entered by the user to configure the source:

```python
class Parameter(NamedModel):
    """Source parameter model."""

    short_name: str | None = None
    help: str | None = None
    help_url: HttpsUrl | None = None
    type: ParameterType
    placeholder: str | None = None
    mandatory: bool = False
    default_value: str | list[str] = ""
    unit: str | None = None
    metrics: list[str] = Field(..., min_items=1)
    values: list[str] | None = None
    api_values: dict[str, str] | None = None
    validate_on: list[str] | None = None
```

Each parameter has a `name` (via `NamedModel`) and a `short_name` used as label in the user interface. The parameter can have a `help` string or a `help_url` (but not both).

The `type` specifies the type of the parameter and the widget used to get user input. Possible values are amongst others `string`, `password`, `integer`, and `multiple_choice`.

The `placeholder` contains text to display in case of multiple choice parameters. For example, in the case of a multiple choice 'severities' parameter with possible values of 'low', 'medium', 'high', the placeholder can be set to 'all severities' to indicate that by default all severities will be measured.

The `mandatory` field indicates whether the parameter is mandatory.

The `default_value` specifies the default value. In case of multiple choice parameters this should be a, possibly empty, list of values.

The `unit` indicates the unit of the parameter. If the `type` is `integer` the `unit` and `min_value` need to be specified.

For each parameter, a list of `metrics` must be given for which the parameter is applicable. This is needed because not every metric needs the same parameters.

If the `type` is `multiple_choice` the possible `values` need to be specified. Also, an `api_values` mapping can specify how the values map to the values used in the API of the source.

The `validate_on` field specifies that the parameter needs to be validated when the parameters in the list change. This can be used to specify that e.g. a URL parameter must be validated when the user changes the password parameter.

##### Entities

Measurement entities are the things that are counted or measured to get the measurement value. For example, the measurement entities of the 'violations' metric are the individual violations. Sometimes, the measurement entities are not interesting enough to show, e.g. when measuring the size in terms of lines of code. In other cases, groups of entities are shown, for example test runs as entities for the 'tests' metric.

The `Entity` and `EntityAttribute` meta models look as follows:

```python
class Entity(BaseModel):
    """Measurement entity (violation, warning, etc.)."""

    name: str = Field(..., regex=r"[a-z]+")
    name_plural: str | None = None
    attributes: list[EntityAttribute]
    measured_attribute: str | None = None


class EntityAttribute(NamedModel):
    """Attributes of measurement entities."""

    key: str | None = None
    help: str | None = None
    url: str | None = None  # Which key to use to get the URL for this attribute
    color: dict[str, Color] | None = None
    type: EntityAttributeType | None = None
    alignment: EntityAttributeAlignment | None = None  # If not given, the alignment is based on the attribute type
    pre: bool | None = None  # Should the attribute be formatted using <pre></pre>? Defaults to False
    visible: bool | None = None  # Should this attribute be visible in the UI? Defaults to True
```

Each entity contains the name (both singular and plural) of the entities and a list of `attributes`.

The attributes are shown as columns in the front end. Each attribute/column consists of a `name` (via `NamedModel`), which is used as column header, and a `key`, used to get the data from the database.

An attribute/column can have a key `url` to specify which field contains the URL to be used in the column. In theory, each column can link to a different URL this way.

To specify the data type of the attribute/column, use the `type` field. If no type is specified, `string` is assumed and no special formatting is applied. Other types supported at the moment are `date`, `datetime`, `float`, `integer`, and `status`. When using `date` or `datetime`, the column should be an ISO-formatted date or date-time string and `Date.toLocaleDateString()` or `Date.toLocaleString()` is used to format the date or date-time.

Values can be mapped to colors using the optional `color` field with a column-value-to-color mapping as value. Possible colors are `positive` (green), `negative` (red), `warning` (yellow) and `active` (grey). These correspond to the possible [states of table rows in Semantic UI React](https://react.semantic-ui.com/collections/table/#states).

Users can mark entities as false positive to ignore them. By default, *Quality-time* subtracts one from the metric value for each ignored entity. However, this would be incorrect if an entity represents a value greater than one, for example when the metric is the amount of ready user story points and each entity is a user story. In that case *Quality-time* can use an attribute of the entity to subtract from the value. The entity field `measured_attribute` determines which attribute to use.

In most cases, the measured attribute is one of the attributes. In other cases, the measured attribute may depend on the parameters selected by the user. For example, when measuring 'tests' using Azure DevOps as source, the test results (failed/passed/etc.) selected by the user influence how many tests *Quality-time* has to subtract from the total if the user decides to ignore a test run. To accommodate this, it is possible to add an attribute that is not shown by the front end, but is used as measured attribute, by marking the attribute as not visible.

Of course, the collector needs to compute the extra attribute and add it to the measurement entities.

#### Subjects

The `subjects` part of the data model is an object where the keys are the subject types and the values are objects describing the subject. The `Subject` meta model looks as follows:

```python
class Subject(DescribedModel):
    """Base model for subjects."""

    metrics: list[str] = Field(..., min_items=1)
```

The `name` is the default name of the subject. The `description` describes the subject type. Both fields are part of `DescribedModel`.

The list of `metrics` contains the metrics that make the most sense for the subject type, and is used for filtering the list of metrics in the dropdown menu of the buttons for moving and copying metrics.

## Proxy

The proxy routes traffic from and to the user's browser. *Quality-time* uses [Nginx](https://nginx.org), but this can be replaced by another proxy if so desired.

The proxy [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/proxy/Dockerfile) adds the *Quality-time* configuration to the Nginx image.

### Health check

As a health check, the favicon is downloaded from the frontend container.

### Environment variables

The proxy uses the following environment variables:

| Name              | Default value | Description                                              |
|:------------------|:--------------|:---------------------------------------------------------|
| `PROXY_PORT`      | `80`          | Port of the proxy, within the internal (Docker) network. |
| `FRONTEND_HOST`   | `frontend`    | The host name of the frontend.                           |
| `FRONTEND_PORT`   | `5000`        | The port the frontend listens on.                        |
| `API_SERVER_HOST` | `api_server`  | The hostname of the API-server.                          |
| `API_SERVER_PORT` | `5001`        | The port the API-server listens on.                      |

## Database

The database component consists of a [MongoDB](https://www.mongodb.com) database to store reports and measurements.

The proxy [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/database/Dockerfile) wraps the {index}`MongoDB` image in a *Quality-time* image so the MongoDB version number can be changed when needed.

*Quality-time* stores its data in a Mongo database using the following collections: `datamodels`, `measurements`, `reports`, `reports_overviews`, and `sessions`.

Data models, reports, and reports overviews are [temporal objects](https://www.martinfowler.com/eaaDev/TemporalObject.html). Every time a new version of the data model is loaded or the user edits a report or the reports overview, an updated copy of the object (a "document" in Mongo-parlance) is added to the collection. Since each copy has a timestamp, this enables the API-server to retrieve the documents as they were at a specific moment in time and provide time-travel functionality.

### Health check

The MongoDB container currently has no health check.

### Environment variables

The database uses the following environment variables:

| Name                         | Default value | Description                |
|:-----------------------------|:--------------|:---------------------------|
| `MONGO_INITDB_ROOT_USERNAME` | `root`        | The MongoDB root username. |
| `MONGO_INITDB_ROOT_PASSWORD` | `root`        | The MongoDB root password. |

## Renderer

The renderer component is used to export quality reports to PDF. *Quality-time* uses [puppeteer](https://github.com/puppeteer/puppeteer).

The renderer [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/renderer/Dockerfile) wraps puppeteer with a small API that uses puppeteer to convert a report URL into a PDF file.

### Health check

The [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/renderer/Dockerfile) contains a health check that uses curl to connect to a health end-point (`/api/health`) of the renderer.

### Environment variables

The renderer uses the following environment variables:

| Name             | Default value | Description                                                                                                                            |
|:-----------------|:--------------|:---------------------------------------------------------------------------------------------------------------------------------------|
| `PROXY_HOST`     | `www`         | Hostname of the proxy. The renderer uses this to access the reports that need to be exported to PDF.                                   |
| `PROXY_PORT`     | `80`          | Port of the proxy, within the internal (Docker) network. The renderer uses this to access the reports that need to be exported to PDF. |
| `PROXY_PROTOCOL` | `http`        | Protocol of the proxy. The renderer uses this to access the reports that need to be exported to PDF.                                   |
| `LC_ALL`         |               | Set the date format in the PDF export. For example, to get DD-MM-YYYY use: `en_GB.UTF-8`.                                              |
| `TZ`             |               | Make the PDF export use the correct timezone. For example, to get Central European Time use: `Europe/Amsterdam`.                       |

## Test data

This component contains test data for the example reports. The Docker image is published as `ictu/quality-time_testdata` on Docker Hub.

### Health check

The test data container currently has no health check.

### Running the test data component

The test data component is started as part of the [Docker-composition](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.override.yml) for development, see the [developer manual](development.md).

To serve the test data locally, you can also start a web server from a console, for example:

```console
python3 -m http.server
```

### Adding test data

Add the example file(s) to the [test data reports](https://github.com/ICTU/quality-time/tree/master/components/testdata/reports) and update one or more of the [example reports](https://github.com/ICTU/quality-time/tree/master/components/shared_code/src/shared/example-reports) in the shared code component.

### Acknowledgements

- `cobertura.xml` was copied from [https://github.com/Bachmann1234/diff_cover/blob/main/diff_cover/tests/fixtures/dotnet_coverage.xml](https://github.com/Bachmann1234/diff_cover/blob/0af9969e5f12420f90f29d8f2c94633b5d2a1aff/tests/fixtures/dotnet_coverage.xml).
- `testng-results.xml` was copied from [https://github.com/richie-b/AtnApiTest/blob/master/test-output/testng-results.xml](https://github.com/richie-b/AtnApiTest/blob/c8ab706bcf386e471488ad94e627eedca613e73e/test-output/testng-results.xml).

## Test LDAP server

A test LDAP server with test users is included for development and testing purposes. An admin interface (phpldapadmin) is included to administer users in this LDAP server.

### Health check

The test LDAP server container currently has no health check.

### LDAP users

The LDAP database has two users:

| User     | Email address         | Username | Password |
|----------|-----------------------|----------|----------|
| Jane Doe | `janedoe@example.org` | `jadoe`  | `secret` |
| John Doe | `johndoe@example.org` | `jodoe`  | `secret` |

The `{ARGON2}` hashes for the `userPassword`s in the LDIF-files were generated using [argon2-cffi](https://github.com/hynek/argon2-cffi):

```python
>>> from argon2 import PasswordHasher
>>> ph = PasswordHasher()
>>> ph.hash("secret")
```
