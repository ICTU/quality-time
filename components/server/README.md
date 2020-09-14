# *Quality-time* server

## Example reports

The [`example-reports`](src/data/example-reports) are imported when the server is started and the database doesn't contain any sample reports yet. Turn off the loading of example report by setting `LOAD_EXAMPLE_REPORTS` to `False`. See the [section on configuration](#configuration) below.

## API

API documentation can be retrieved via http://www.quality-time.example.org/api (all versions, all routes), http://www.quality-time.example.org/api/v2 (all routes for a specific version, in this case version 2), and http://www.quality-time.example.org/api/v2/<route_fragment> (all routes matching a specific text fragment).

## Data model

The [`datamodel.json`](src/data/datamodel.json) describes the domain model used by the application. It allows for a frontend that doesn't need to know about specific metrics and sources. Every time the server is started, the latest data model is imported into the database. The server [`data` package](src/data/datamodel.json) contains the `datamodel.json`.

The data model consists of five parts:

- Entities
- Scales
- Metrics
- Sources
- Subjects

### Entities

Measurement entities are the things that are counted or measured to get the measurement value. For example, the measurement entities of the 'violations' metric are the individual violations. Sometimes, the measurement entities are not interesting enough to show, e.g. when measuring the size in terms of lines of code. In other cases, groups of entities are shown, for example test runs as entities for the 'tests' metric.

The data model contains a top-level object that describes generic information about the entities. Each source also has a specification of entities for each metric that the source supports, see the [source entities](#source-entities) section below.

The top-level entities object contains the possible statuses (unconfirmed, confirmed, fixed, won't fix, and false positive) that entities can have:

```json
{
    "entities": {
        "statuses": {
            "unconfirmed": {
                "default": true,
                "name": "Unconfirmed",
                "description": "This ${entity_type} should be reviewed to decide what to do with it.",
                "action": "Unconfirm",
                "ignore_entity": false
            },
            "confirmed": {
                "default": true,
                "name": "Confirmed",
                "description": "..."
            }
        }
    }
}
```

For each status, the `default` flag specifies whether the status should be used for source entities that don't specify which statuses they allow. The `name` field gives the name of the status. The `description` describes the status and should use one parameter `${entity_type}` that is replaced by the actual entity type (e.g. violation, security warning or user story) in the UI. The `action` describes the change that would result in the status, e.g. the 'confirm' action leads to the 'confirmed' status. Finally, the `ignore_entity` flag specifies whether entities with this state should be ignored and subtracted from the measurement value.

### Scales

The `scales` part of the data model defines the scales uses. At the time of writing these include an absolute count scale and a percentage scale.

```json
{
    "scales": {
       "count": {
           "name": "Count",
           "description": "..."
       },
       "percentage": {
           "name": "Percentage",
           "description": "..."
       }
    }
}
```

Each metric defines the scales it supports.

### Metrics

The `metrics` part of the data model is an object where the keys are the metric types and the values are objects describing the metric type. A metric type, for example the `complex_units` metric, is described as follows:

```json
{
    "metrics": {
        "complex_units": {
            "name": "Complex units",
            "description": "Measure the number of units (classes, functions, methods, files) that are too complex.",
            "scales": [
                "count",
                "percentage"
            ],
            "default_scale": "count",
            "unit": "complex units",
            "addition": "sum",
            "direction": "<",
            "target": "0",
            "near_target": "10",
            "sources": [
                "hq",
                "sonarqube",
                "random"
            ],
            "tags": [
                "maintainability",
                "testability"
            ]
        }
    }
}
```

The `name` is the default name of metrics of this type. The `description` describes what the metric measures. The `scales` list shows which scales the metric supports and the `default_scale` specifies which scale is the default scale. The `unit` is the default unit of the metric, e.g. lines of code, security warnings, or in the above example, complex units. The `addition` determines how values from multiple sources are combined: possible values are `max`, `min`, and `sum`. The `direction` specifies whether smaller measurement values are better or worse. The `target` is the default target value for the metric. The `near_target` is when the metric becomes red. Values between `target` and `near_target` are yellow. The list of `sources` contains the keys of source types that support this metric type. Finally, `tags` are simple strings used to group related metrics.

Users with sufficient rights can override the default name, unit, and target of metrics via the user interface.

### Sources

The `sources` part of the data model is an object where the keys are the source types and the values are objects describing the source. A source, for example the `azure_devops` source type, is described as follows:

```json
{
    "sources": {
        "azure_devops": {
            "name": "Azure DevOps Server",
            "description": "Azure DevOps Server (formerly known as Team Foundation Server) by Microsoft provides source code management, reporting, requirements management, project management, automated builds, testing and release management.",
            "url": "https://azure.microsoft.com/en-us/services/devops/server/",
            "parameters": {
                "url": {
                    "name": "URL",
                    "type": "string",
                    "default_value": "",
                    "metrics": [
                        "issues"
                    ]
                },
                "private_token": {
                    "name": "Private Token",
                    "type": "password",
                    "help_url": "https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops",
                    "default_value": "",
                    "metrics": [
                        "issues"
                    ]
                },
                "wiql": {
                    "name": "Issue query in WIQL (Work Item Query Language)",
                    "type": "string",
                    "help_url": "https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops",
                    "default_value": "",
                    "metrics": [
                        "issues"
                    ]
                },
                "test_result": {
                    "name": "Test result",
                    "type": "multiple_choice",
                    "mandatory": false,
                    "default_value": "",
                    "values": [
                        "incomplete",
                        "failed",
                        "not applicable",
                        "passed"
                    ],
                    "api_values": {
                        "incomplete": "incompleteTests",
                        "failed": "unanalyzedTests",
                        "passed": "passedTests",
                        "not applicable": "notApplicableTests"
                    },
                    "metrics": [
                        "tests"
                    ]
                }
            },
            "entities": {
                "issues": {
                    "name": "issue",
                    "name_plural": "issues",
                    "attributes": [                
                        {
                            "name": "Project",
                            "key": "project"
                        },
                        {
                            "name": "Title",
                            "key": "title",
                            "url": "url"
                        },
                        {
                            "name": "Work item type",
                            "key": "work_item_type"
                        },
                        {
                            "name": "State",
                            "key": "state",
                            "color": {
                                "error": "negative",
                                "warning": "warning"
                            }
                        },
                        {
                            "name": "Date of last update",
                            "key": "last_update",
                            "type": "datetime"
                        }
                    ]
                }
            }
        }
    }
}
```

The `name` is the default name of sources of this type. The `description` gives some background information on the source type. The `url` links to a landing page describing the source type.

#### Source parameters

The `parameters` describe the parameters that need to be entered by the user to configure the source. Each parameter has a `name` used as label in the user interface. The `type` specifies the type of the parameter and the widget used to get user input. Possible values are `string`, `password`, `integer`, and `multiple_choice`. If the `type` is `integer` the `unit` and `min_value` need to be specified and optionally a `max_value`. If the `type` is `multiple_choice` the possible `values` need to be specified. A `default_value` can also be given. Also, an `api_values` mapping can specify how the values map to the values used in the API of the source. Finally, for each parameter, a list of `metrics` must be given for which the parameter is applicable. This is needed because not every metric needs the same parameters.

#### Source entities

The `entities` object contains the name (both singular and plural) of the entities and a list of `attributes`. The attributes are shown as columns in the front end. Each attribute/column consists of a `name`, which is used as column header, and a `key`, used to get the data from the database. An attribute/column can have a key `url` to specify which field contains the url to be used in the column. In theory, each column can link to a different url this way. To specify the data type of the attribute/column, use the `type` key. If no type is specified, `string` is assumed and no special formatting is applied. Other types supported at the moment are `date`, `datetime`, `float`, `integer`, and `status`. When using `date` or `datetime`, the column should be an ISO-formatted date or datetime string and `Date.toLocaleDateString()` or `Date.toLocaleString()` is used to format the date or datetime. Values can be mapped to colors using the optional `color` key with a column-value-to-color mapping as value. Possible colors are `positive` (green), `negative` (red), `warning` (yellow) and `active` (grey). These correspond to the possible [states of table rows in Semantic UI React](https://react.semantic-ui.com/collections/table/#states). 

Users can mark entities as false positive to ignore them. By default *Quality-time* subtracts one from the metric value for each ignored entity. However, this would be incorrect if an entity represents a value greater than one, for example when the metric is the amount of ready user story points and each entity is a user story. In that case *Quality-time* can use an attribute of the entity to subtract from the value. The attribute `measured_attribute` determines which attribute to use:

```json
{
    "sources": {
        "azure_devops": {
            "entities": {
                "ready_user_story_points": {
                   "name": "user story",
                   "name_plural": "user stories",
                   "measured_attribute": "points",
                   "attributes": [
                       {
                          "name": "Summary",
                          "key": "summary",
                          "url": "url"
                       },
                       {
                          "name": "Points",
                          "key": "points",
                          "type": "float"
                       }
                   ]
               }
            }
        }
    }
}
```

In most cases, the measured attribute is simply one of the attributes. In other cases, the measured attribute may depend on the parameters selected by the user. For example, when measuring 'tests' using Azure DevOps as source, the test results (failed/passed/etc.) selected by the user influence how many tests *Quality-time* has to subtract from the total if the user decides to ignore a test run. To accommodate this, it is possible to add an attribute that is not shown by the front end, but is used as measured attribute:

```json
{
    "sources": {
        "azure_devops": {
            "entities": {
                "tests": {
                    "name": "test run",
                    "name_plural": "test runs",
                    "measured_attribute": "counted_tests",
                    "attributes": [
                        {
                            "name": "Test run name",
                            "key": "name"
                        },
                        {
                            "name": "Passed tests",
                            "key": "passed_tests",
                            "type": "integer"
                        },
                        {
                            "name": "Failed tests",
                            "key": "unanalyzed_tests",
                            "type": "integer"
                        },
                        {
                            "name": "Total tests",
                            "key": "total_tests",
                            "type": "integer"
                        },
                        {
                            "name": "Counted tests",
                            "key": "counted_tests",
                            "type": "integer",
                            "visible": false
                        }
                    ]
                }
            }
        }
    }
}
```

Of course, the collector needs to compute the extra attribute and add it to the measurement entities.

## Subjects

The `subjects` part of the data model is an object where the keys are the subject types and the values are objects describing the subject type. A subject type, for example the `software` subject, is described as follows:

```json
{
    "subjects": {
        "software": {
            "name": "Software",
            "description": "A custom software application or component.",
            "metrics": [
                "complex_units",
                "duplicated_lines",
                "failed_tests",
                "..."
            ]
        }
    }
}
```

The `name` is the default name of the subject. The `description` describes the subject type. The list of `metrics` contains the metrics that make the most sense for the subject type, and is used for filtering the list of metrics in the dropdown menu of the buttons for moving and copying metrics.

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
