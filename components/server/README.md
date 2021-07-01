# *Quality-time* server

## Example reports

The [`example-reports`](src/example-reports) are imported when the server is started and the database doesn't contain any sample reports yet. Turn off the loading of example report by setting `LOAD_EXAMPLE_REPORTS` to `False`. See the [section on configuration](#configuration) below.

## API

API documentation can be retrieved via http://www.quality-time.example.org/api (all versions, all routes), http://www.quality-time.example.org/api/v2 (all routes for a specific version, in this case version 2), and http://www.quality-time.example.org/api/v2/<route_fragment> (all routes matching a specific text fragment).

## Data model

The data model package describes the domain model used by the application. It allows for a frontend that doesn't need to know about specific metrics and sources. On server start up, it checks whether the data model has changed, and if so, imports it into the database.

The data model package consists of a meta model and the data model itself. The data model consists of four major parts:

- Scales
- Metrics
- Sources
- Subjects

The meta model uses Pydantic to specify the components and attributes of the data model.

### Scales

The `scales` part of the data model defines the scales that can be used to measure metrics. At the time of writing these include an absolute count scale, a percentage scale, and a version number scale.

Each metric defines the scales it supports.

### Metrics

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

### Sources

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

#### Configuration

In cases where *Quality-time* needs information about sources that doesn't need to be parameterizable, `Configurations` can be added to the source. A configuration consists of a name (via `NamedModel`), a list of metrics to which the configuration applies, and a value:

```python
class Configuration(NamedModel):  # pylint: disable=too-few-public-methods
    """Configuration for specific metrics."""

    metrics: list[str] = Field(..., min_items=1)
    value: list[str] = Field(..., min_items=1)
```

#### Parameters

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

#### Entities

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

## Subjects

The `subjects` part of the data model is an object where the keys are the subject types and the values are objects describing the subject. The `Subject` meta model looks as follows:

```python
class Subject(DescribedModel):
    """Base model for subjects."""

    metrics: list[str] = Field(..., min_items=1)
```

The `name` is the default name of the subject. The `description` describes the subject type. Both fields are part of `DescribedModel`.

The list of `metrics` contains the metrics that make the most sense for the subject type, and is used for filtering the list of metrics in the dropdown menu of the buttons for moving and copying metrics.

## Database collections

*Quality-time* stores its data in a Mongo database using the following collections: `datamodels`, `measurements`, `reports`, `reports_overviews`, and `sessions`.
The server component is the only component that directly interacts with the database. The server [`database` package](src/database) contains the code for interacting with the collections.

Data models, reports, and reports overviews are [temporal objects](https://www.martinfowler.com/eaaDev/TemporalObject.html). Every time a new version of the data model is loaded or the user edits a report or the reports overview, an updated copy of the object (a "document" in Mongo-parlance) is added to the collection. Since each copy has a timestamp, this enables the server to retrieve the documents as they were at a specific moment in time.

## Health check

The [Dockerfile](Dockerfile) contains a health check that uses curl to retrieve an API (api/health) from the server. Officially, this API does not exist, but since the server simply returns an empty JSON file it works for checking the health of the server.

## Configuration

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
