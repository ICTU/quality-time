# Software documentation

This document describes the *Quality-time* software. It is aimed at *Quality-time* developers and maintainers.

```{eval-rst}
.. graphviz:: components-dark.dot
   :class: only-dark

.. graphviz:: components-light.dot
   :class: only-light
```

*Quality-time* consists of seven components.

Four bespoke components:

- A [frontend](#frontend) serving the React UI,
- A [server](#server) serving the API,
- A [collector](#collector) to collect the measurements from the sources.
- A [notifier](#notifier) to notify users about events such as metrics turning red.

And three standard components:

- A [proxy](#proxy) routing traffic from and to the user's browser,
- A [database](#database) for storing reports and measurements,
- A renderer (we use the [ICTU variant of url-to-pdf-api](https://github.com/ICTU/url-to-pdf-api)) to export reports to PDF,

In addition, unless forward authentication is used, an LDAP server is expected to be available to authenticate users.

For testing purposes there are also [test data](#test-data) and an [test LDAP server](#test-ldap-server).

## Frontend

The frontend contains the React frontend code. This component was bootstrapped using [Create React App](https://github.com/ICTU/quality-time/blob/master/components/frontend/README-Create-React-App.md).

### Health check

As a health check, the favicon is downloaded.

### Configuration

The frontend uses the following environment variables:

| Name | Default value | Description |
| :--- | :---------- | :------------ |
| FRONTEND_PORT | 5000 | The port the frontend listens on. |

## Server

### Example reports

The [`example-reports`](https://github.com/ICTU/quality-time/tree/master/components/server/src/external/example-reports) are imported when the server is started and the database doesn't contain any sample reports yet. Turn off the loading of example report by setting `LOAD_EXAMPLE_REPORTS` to `False`. See the [section on configuration](#configuration) below.

```{index} API
```

### API

API documentation can be retrieved via http://www.quality-time.example.org/api (all versions, all routes), http://www.quality-time.example.org/api/v2 (all routes for a specific version, in this case version 2), and http://www.quality-time.example.org/api/v2/<route_fragment> (all routes matching a specific text fragment).

### Data model

The data model package describes the domain model used by the application. It allows for a frontend that doesn't need to know about specific metrics and sources. On server start up, it checks whether the data model has changed, and if so, imports it into the database.

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

    scales: list[str] = Field(["count"], min_items=1)
    default_scale: str = "count"
    unit: Unit = Unit.NONE
    addition: Addition = Addition.SUM
    direction: Direction = Direction.FEWER_IS_BETTER
    target: str = "0"
    near_target: str = "10"
    sources: list[str] = Field(..., min_items=1)
    default_source: Optional[str] = None
    tags: list[Tag] = []
```

The `name` is the default name of metrics of this type. The `description` describes what the metric measures. These are part of the `DescribedModel`.

The `scales` list shows which scales the metric supports and the `default_scale` specifies which scale is the default scale.

The `unit` is the default unit of the metric, e.g. lines of code, security warnings, or in the above example, complex units.

The `addition` determines how values from multiple sources are combined: possible values are `max`, `min`, and `sum`.

The `direction` specifies whether smaller measurement values are better or worse.

The `target` is the default target value for the metric. The `near_target` is when the metric becomes red. Values between `target` and `near_target` are yellow.

The list of `sources` contains the keys of source types that support this metric type.

Finally, `tags` are strings used to group related metrics.

Users with sufficient rights can override the default name, unit, and target of metrics via the user interface.

#### Sources

The `sources` part of the data model is a dictionary that describes all supported source types. The keys are the source type names. The values are objects describing the source type. All source types have the following meta model:

```python
class Source(DescribedModel):
    """The source model extends the base model with source parameters and measurement entities."""

    url: Optional[HttpUrl] = None
    configuration: Optional[Configurations] = None
    parameters: Parameters
    entities: Entities = cast(Entities, {})

```

The `name` is the default name of sources of this type. The `description` gives some background information on the source type. These are part of the `DescribedModel`.

The `url` links to a landing page describing the source type.

##### Configuration

In cases where *Quality-time* needs information about sources that doesn't need to be parameterizable, `Configurations` can be added to the source. A configuration consists of a name (via `NamedModel`), a list of metrics to which the configuration applies, and a value:

```python
class Configuration(NamedModel):  # pylint: disable=too-few-public-methods
    """Configuration for specific metrics."""

    metrics: list[str] = Field(..., min_items=1)
    value: list[str] = Field(..., min_items=1)
```

##### Parameters

The `parameters` describe the parameters that need to be entered by the user to configure the source:

```python
class Parameter(NamedModel):
    """Source parameter model."""

    short_name: Optional[str] = None
    help: Optional[str] = Field(None, regex=r".+\.")
    help_url: Optional[HttpUrl] = None
    type: ParameterType
    placeholder: Optional[str] = None
    mandatory: bool = False
    default_value: Union[str, list[str]] = ""
    unit: Optional[str] = None
    metrics: list[str] = Field(..., min_items=1)
    values: Optional[list[str]] = None
    api_values: Optional[dict[str, str]] = None
    validate_on: Optional[list[str]] = None
```

Each parameter has a `name` (via `NamedModel`) and a `short_name` used as label in the user interface. The parameter can have a `help` string or a `help_url` (but not both).

The `type` specifies the type of the parameter and the widget used to get user input. Possible values are amongst others `string`, `password`, `integer`, and `multiple_choice`.

The `placeholder` contains text to display in case of multiple choice parameters. For example, in the case of a multiple choice 'severities' parameter with possible values of 'low', 'medium', 'high', the placeholder can be set to 'all severities' to indicate that by default all severities will be measured.

The `mandatory` field indicates whether the parameter is mandatory.

The `default_value` specifies the default value. In case of multiple choice parameters this should be a, possibly empty, list of values.

The `unit` indicates the unit of the parameter. If the `type` is `integer` the `unit` and `min_value` need to be specified.

For each parameter, a list of `metrics` must be given for which the parameter is applicable. This is needed because not every metric needs the same parameters.

If the `type` is `multiple_choice` the possible `values` need to be specified. Also, an `api_values` mapping can specify how the values map to the values used in the API of the source.

The `validate_on` field specifies that the parameter needs to be validated when the parameters in the list change. This can be used to specify that e.g. a url parameter must be validated when the user changes the password parameter.

##### Entities

Measurement entities are the things that are counted or measured to get the measurement value. For example, the measurement entities of the 'violations' metric are the individual violations. Sometimes, the measurement entities are not interesting enough to show, e.g. when measuring the size in terms of lines of code. In other cases, groups of entities are shown, for example test runs as entities for the 'tests' metric.

The `Entity` and `EntityAttribute` meta models look as follows:

```python
class Entity(BaseModel):
    """Measurement entity (violation, warning, etc.)."""

    name: str = Field(..., regex=r"[a-z]+")
    name_plural: Optional[str] = None
    attributes: list[EntityAttribute]
    measured_attribute: Optional[str] = None


class EntityAttribute(NamedModel):
    """Attributes of measurement entities."""

    key: Optional[str] = None
    url: Optional[str] = None
    color: Optional[dict[str, Color]] = None
    type: Optional[EntityAttributeType] = None
    pre: Optional[bool] = None
    visible: Optional[bool] = None
```

Each entity contains the name (both singular and plural) of the entities and a list of `attributes`.

The attributes are shown as columns in the front end. Each attribute/column consists of a `name` (via `NamedModel`), which is used as column header, and a `key`, used to get the data from the database.

An attribute/column can have a key `url` to specify which field contains the url to be used in the column. In theory, each column can link to a different url this way.

To specify the data type of the attribute/column, use the `type` field. If no type is specified, `string` is assumed and no special formatting is applied. Other types supported at the moment are `date`, `datetime`, `float`, `integer`, and `status`. When using `date` or `datetime`, the column should be an ISO-formatted date or datetime string and `Date.toLocaleDateString()` or `Date.toLocaleString()` is used to format the date or datetime.

Values can be mapped to colors using the optional `color` field with a column-value-to-color mapping as value. Possible colors are `positive` (green), `negative` (red), `warning` (yellow) and `active` (grey). These correspond to the possible [states of table rows in Semantic UI React](https://react.semantic-ui.com/collections/table/#states).

Users can mark entities as false positive to ignore them. By default, *Quality-time* subtracts one from the metric value for each ignored entity. However, this would be incorrect if an entity represents a value greater than one, for example when the metric is the amount of ready user story points and each entity is a user story. In that case *Quality-time* can use an attribute of the entity to subtract from the value. The entity field `measured_attribute` determines which attribute to use.

In most cases, the measured attribute is simply one of the attributes. In other cases, the measured attribute may depend on the parameters selected by the user. For example, when measuring 'tests' using Azure DevOps as source, the test results (failed/passed/etc.) selected by the user influence how many tests *Quality-time* has to subtract from the total if the user decides to ignore a test run. To accommodate this, it is possible to add an attribute that is not shown by the front end, but is used as measured attribute, by marking the attribute as not visible.

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

### Database collections

*Quality-time* stores its data in a Mongo database using the following collections: `datamodels`, `measurements`, `reports`, `reports_overviews`, and `sessions`.

The server component is the only component that directly interacts with the database. The server [`database` package](https://github.com/ICTU/quality-time/tree/master/components/server/src/external/database) contains the code for interacting with the collections.

Data models, reports, and reports overviews are [temporal objects](https://www.martinfowler.com/eaaDev/TemporalObject.html). Every time a new version of the data model is loaded or the user edits a report or the reports overview, an updated copy of the object (a "document" in Mongo-parlance) is added to the collection. Since each copy has a timestamp, this enables the server to retrieve the documents as they were at a specific moment in time.

### Health check

The [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/server/Dockerfile) contains a health check that uses curl to retrieve an API (api/health) from the server. Officially, this API does not exist, but since the server simply returns an empty JSON file it works for checking the health of the server.

### Configuration

The server uses the following environment variables:

| Name | Default value | Description |
| :--- | :---------- | :------------ |
| SERVER_PORT | 5001 | Port of the server. |
| PROXY_HOST | www | Hostname of the proxy. The server uses this to construct URLs to pass to the renderer for exporting reports to PDF. |
| PROXY_PORT | 80 | Port of the proxy. The server uses this to construct URLs to pass to the renderer for exporting reports to PDF. |
| DATABASE_URL | mongodb://root:root@database:27017 | Mongo database connection URL. |
| LDAP_URL | ldap://ldap:389 | LDAP connection URL. |
| LDAP_ROOT_DN | dc=example,dc=org | LDAP root distinguished name. |
| LDAP_LOOKUP_USER_DN | cn=admin,dc=example,dc=org | LDAP lookup user distinguished name. |
| LDAP_LOOKUP_USER_PASSWORD | admin | LDAP lookup user password. |
| LDAP_SEARCH_FILTER | (&#124;(uid=$$username)(cn=$$username)) | LDAP search filter. With this default search filter, users can use either their LDAP canonical name (`cn`) or their LDAP user id to login. The `$username` variable is filled by *Quality-time* at run time with the username that the user enters in the login dialog box. |
| LOAD_EXAMPLE_REPORTS | True | Whether or not to import example reports in the database on start up. |

## Collector

The collector is responsible for collecting measurement data from sources. It wakes up once every minute and asks the server for a list of all metrics. For each metric, the collector gets the measurement data from each of the metric's sources and posts a new measurement to the server.

If a metric has been recently measured and its parameters haven't been changed, the collector skips the metric.

### Health check

Every time the collector wakes up, it writes the current date and time in ISO format to the 'health_check.txt' file. This date and time is read by the Docker health check (see the [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/collector/Dockerfile)). If the written date and time are too long ago, the collector container is considered to be unhealthy.

### Configuration

The collector uses the following environment variables:

| Name | Default value | Description |
| :--- | :---------- | :------------ |
| SERVER_HOST | server | Hostname of the server. The collector uses this to get the metrics and post the measurements. |
| SERVER_PORT | 5001 | Port of the server. The collector uses this to get the metrics and post the measurements. |
| COLLECTOR_SLEEP_DURATION | 20 | The maximum amount of time (in seconds) that the collector sleeps between collecting measurements. |
| COLLECTOR_MEASUREMENT_LIMIT | 30 | The maximum number of metrics that the collector measures each time it wakes up. If more metrics need to be measured, they will be measured the next time the collector wakes up. |
| COLLECTOR_MEASUREMENT_FREQUENCY | 900 | The amount of time (in seconds) after which a metric should be measured again. |

## Notifier

The notifier is responsible for notifying users about significant events, such as metrics turning red. It wakes up periodically and asks the server for all reports. For each report, the notifier determines whether whether notification destinations have been configured, and whether events happened that need to be notified.

### Health check

Every time the notifier wakes up, it writes the current date and time in ISO format to the 'health_check.txt' file. This date and time is read by the Docker health check (see the [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/notifier/Dockerfile)). If the written date and time are too long ago, the notifier container is considered to be unhealthy.

### Configuration

| Name | Default value | Description |
| :--- | :---------- | :------------ |
| SERVER_HOST | server | Hostname of the server. The notifier uses this to get the metrics. |
| SERVER_PORT | 5001 | Port of the server. The notifier uses this to get the metrics. |
| NOTIFIER_SLEEP_DURATION | 60 | The amount of time (in seconds) that the notifier sleeps between sending notifications. |

## Proxy

The proxy routes traffic from and to the user's browser. *Quality-time* uses the [ICTU variant of Caddy](https://github.com/ICTU/caddy) as proxy, but this can be replaced by another proxy if so desired.

The proxy [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/proxy/Dockerfile) simply wraps the Caddy image in a *Quality-time* image so the Caddy version number can be changed when needed.

## Database

The database component consists of a [Mongo](https://www.mongodb.com) database to store reports and measurements.

The proxy [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/database/Dockerfile) simply wraps the MongoDB image in a *Quality-time* image so the MongoDB version number can be changed when needed.

## Renderer

The renderer component is used to export quality reports to PDF. *Quality-time* uses the [ICTU variant of url-to-pdf-api](https://github.com/ICTU/url-to-pdf-api).

The renderer [Dockerfile](https://github.com/ICTU/quality-time/blob/master/components/renderer/Dockerfile) simply wraps the ictu/url-to-pdf-api image in a *Quality-time* image so the version number can be changed when needed.

## Test data

This component contains test data for the example reports. The Docker image is published as `ictu/quality-time_testdata` on Docker Hub.

### Running the test data component

The test data component is started as part of the [docker composition](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.override.yml) for development, see the [developer manual](development.md).

To serve the test data locally, you can also simply start a webserver, e.g.:

```console
python3 -m http.server
```

### Adding test data

Add the example file(s) to the [test data reports](https://github.com/ICTU/quality-time/tree/master/components/testdata/reports) and update one or more of the [example reports](https://github.com/ICTU/quality-time/tree/master/components/server/src/example-reports) in the server component.

### Acknowledgements

- `cobertura.xml` was copied from [https://github.com/Bachmann1234/diff_cover/blob/main/diff_cover/tests/fixtures/dotnet_coverage.xml](https://github.com/Bachmann1234/diff_cover/blob/0af9969e5f12420f90f29d8f2c94633b5d2a1aff/tests/fixtures/dotnet_coverage.xml).
- `testng-results.xml` was copied from [https://github.com/richie-b/AtnApiTest/blob/master/test-output/testng-results.xml](https://github.com/richie-b/AtnApiTest/blob/c8ab706bcf386e471488ad94e627eedca613e73e/test-output/testng-results.xml).

## Test LDAP server

The [test LDAP server](https://github.com/ICTU/quality-time/tree/master/components/ldap) is included for test purposes. It is based on the `osixia/openldap` Docker image, and adds two extra users. The Docker image is published as `ictu/quality-time_testldap` on Docker Hub.

### LDAP users

The LDAP database has two (*) users:

| User          | Email address       | Username | Password |
| ------------- | ------------------- | -------- | -------- |
| Jane Doe      | janedoe@example.org | jadoe    | secret   |
| John Doe      | johndoe@example.org | jodoe    | secret   |

(*) The `osixia/openldap` Docker image normally has an administrator user as well, but due to [this issue in OpenLDAP 1.5.0](https://github.com/osixia/docker-openldap/issues/555) this user is currently not available.
