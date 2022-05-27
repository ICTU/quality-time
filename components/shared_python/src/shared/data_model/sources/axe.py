"""Axe sources."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, MultipleChoiceParameter, MultipleChoiceWithAdditionParameter


ALL_AXE_CORE_METRICS = ["accessibility", "source_up_to_dateness", "source_version"]


IMPACT = MultipleChoiceParameter(
    name="Impact levels",
    help="If provided, only count accessibility violations with the selected impact levels.",
    placeholder="all impact levels",
    values=["minor", "moderate", "serious", "critical"],
    metrics=["accessibility"],
)

TAGS_TO_INCLUDE = MultipleChoiceWithAdditionParameter(
    name="Tags to include (regular expressions or tags)",
    short_name="tags to include",
    help="Tags to include can be specified by tag or by regular expression.",
    placeholder="all",
    metrics=["accessibility"],
)

TAGS_TO_IGNORE = MultipleChoiceWithAdditionParameter(
    name="Tags to ignore (regular expressions or tags)",
    short_name="tags to ignore",
    help="Tags to ignore can be specified by tag or by regular expression.",
    metrics=["accessibility"],
)

RESULT_TYPES = MultipleChoiceParameter(
    name="Result types",
    help="Limit which result types to count.",
    default_value=["violations"],
    placeholder="all result types",
    values=["inapplicable", "incomplete", "passes", "violations"],
    metrics=["accessibility"],
)

ENTITIES = dict(
    accessibility=dict(
        name="accessibility violation",
        attributes=[
            dict(name="Violation type", url="help"),
            dict(
                name="Result type",
                color=dict(
                    passes=Color.POSITIVE,
                    violations=Color.NEGATIVE,
                    inapplicable=Color.ACTIVE,
                    incomplete=Color.WARNING,
                ),
            ),
            dict(name="Impact"),
            dict(name="Page of the violation", key="page", url="url"),
            dict(name="Element"),
            dict(name="Description"),
            dict(name="Tags"),
        ],
    )
)

AXE_CORE_DOCUMENTATION = """
When running Axe-core on a webpage, the
[run function](https://github.com/dequelabs/axe-core/blob/develop/doc/API.md#api-name-axerun) returns a
[results object](https://github.com/dequelabs/axe-core/blob/develop/doc/API.md#results-object). The results objects
may be stored in separate JSON files and served to *Quality-time* in a zipfile, or the results objects can be combined
in one JSON file that contains a list of results objects.
"""

AXE_CORE = Source(
    name="Axe-core",
    description="Axe is an accessibility testing engine for websites and other HTML-based user interfaces.",
    url="https://github.com/dequelabs/axe-core",
    documentation=dict(
        accessibility=AXE_CORE_DOCUMENTATION,
        source_up_to_dateness=AXE_CORE_DOCUMENTATION
        + """
Axe-core adds a `timestamp` field to each results object. That field is used by *Quality-time* to determine the
up-to-dateness of the report. If there is more than one results object in the JSON file, *Quality-time* uses the
first one it encounters, assuming that all timestamps in one JSON file will be roughly equal.

```{tip}
When combining results objects, make sure the `timestamp` field is retained in the JSON.
```
""",
        source_version=AXE_CORE_DOCUMENTATION
        + """
Axe-core adds a `testEngine` field to each results object. That field is used by *Quality-time* to determine the
version of Axe-core used to generate the report. If there is more than one results object in the JSON file,
*Quality-time* uses the first one it encounters, assuming that all test engines used in one JSON file will be equal.

```{tip}
When combining results objects, make sure the `testEngine` field is retained in the JSON.
```
""",
    ),
    parameters=dict(
        tags_to_include=TAGS_TO_INCLUDE,
        tags_to_ignore=TAGS_TO_IGNORE,
        impact=IMPACT,
        result_types=RESULT_TYPES,
        **access_parameters(ALL_AXE_CORE_METRICS, source_type="an Axe-core report", source_type_format="JSON")
    ),
    entities=ENTITIES,
)

AXE_HTML_REPORTER = Source(
    name="Axe HTML reporter",
    description="Creates an HTML report from the axe-core library AxeResults object.",
    url="https://www.npmjs.com/package/axe-html-reporter",
    parameters=dict(
        tags_to_include=TAGS_TO_INCLUDE,
        tags_to_ignore=TAGS_TO_IGNORE,
        impact=IMPACT,
        result_types=RESULT_TYPES,
        **access_parameters(["accessibility"], source_type="an Axe report", source_type_format="HTML")
    ),
    entities=ENTITIES,
)

AXE_CSV = Source(
    name="Axe CSV",
    description="An Axe accessibility report in CSV format.",
    url="https://github.com/ICTU/axe-reports",
    parameters=dict(
        impact=IMPACT, **access_parameters(["accessibility"], source_type="an Axe report", source_type_format="CSV")
    ),
    entities=dict(
        accessibility=dict(
            name="accessibility violation",
            attributes=[
                dict(name="Violation type", url="help"),
                dict(name="Impact"),
                dict(name="Page of the violation", key="page", url="url"),
                dict(name="Element"),
                dict(name="Description"),
            ],
        )
    ),
)
