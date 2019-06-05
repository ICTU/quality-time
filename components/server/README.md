# Quality-time server

## Example reports

The [`example-reports`](example-reports) are imported when the server is started and the database doesn't contain any sample reports yet.

## Data model

The [`datamodel.json`](datamodel.json) describes the domain model used by the application. It allows for a frontend that doesn't need to know about specific metrics and sources. Everytime the server is started, the latest datamodel is imported into the database.

The datamodel consists of three parts:

- Metrics
- Sources
- Subjects

### Metrics

The `metrics` part of the datamodel is an object where the keys are the metric types and the values are objects describing the metric type. A metric type, for example the `complex_units` metric, is described as follows:

```json
{
    "metrics": {
        "complex_units": {
            "name": "Complex units",
            "description": "Measure the number of units (classes, functions, methods, files) that are too complex.",
            "unit": "complex units",
            "addition": "sum",
            "direction": "<=",
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

The `name` is the default name of metrics of this type. The `description` describes what the metric measures. The `unit` is the default unit of the metric, e.g. lines of code, security warnings, or in the above example, complex units. The `addition` determines how values from multiple sources are combined: possible values are `sum` and `max`. The `direction` specifies whether smaller measurement values are better or worse. The `target` is the default target value for the metric. The `near_target` is when the metric becomes red. Values between `target` and `near_target` are yellow. The list of `sources` contains the keys of source types that support this metric type. Finally, `tags` are simple strings used to group related metrics.

Users with sufficient rights can override the default name, unit, and target of metrics via the user interface.

### Sources

The `sources` part of the datamodel is an object where the keys are the source types and the values are objects describing the source. A source, for example the `azure_devops` source type, is described as follows:

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
                }
            },
            "entities": {
                "issues": [
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
                        "key:": "last_update",
                        "type": "datetime"
                    }
                ]
            }
        }
    }
}
```

The `name` is the default name of sources of this type. The `description` gives some background information on the source type. The `url` links to a landing page describing the source type.

The `parameters` describe the parameters that need to be entered by the user to configure the source. Each parameter has a `name` used as label in the user interface. The `type` specifies the type of the parameter and the widget used to get user input. Possible values are `string`, `password`, `integer`, and `multiple_choice`. If the `type` is `integer` the `unit` needs to be specified. If the `type` is `multiple_choice` the possible `values` need to be specified. A `default_value` can also be given. Finally, for each parameter, a list of `metrics` must be given for which the parameter is applicable. This is needed because not every metric needs the same parameters.

The `entities` object contains a list of columns to be used to display the entities of the metric. Each column consists of a `name`, which is used as column header, and a `key`, used to get the data from the database. The key `url` can be used to specify which field contains the url to be used in the column. In theory, each column can link to a different url this way. To specify the data type of the column, use the `type` key. If no type is specified, `string` is assumed and no special formatting is applied. The only other types supported at the moment are `date` and `datetime`. The column should be an ISO-formatted date or datetime string and `Date.toLocaleDateString()` or `Date.toLocaleString()` is used to format the date or datetime. Values can be mapped to colors using the `color` key with a column-value-to-color mapping as value. Possible colors are `positive` (green), `negative` (red), `warning` (yellow) and `active` (grey). These correspond to the possible [states of table rows in Semantic UI React](https://react.semantic-ui.com/collections/table/#states).

## Subjects

The `subjects` part of the datamodel is an object where the keys are the subject types and the values are objects describing the subject type. A subject type, for example the `software` subject, is described as follows:

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

The `name` is the default name of the subject. The `description` describes the subject type. The list of `metrics` contains the metrics that make the most sense for the subject type, but that information isn't used at the moment.
