"""SonarQube source."""

from pydantic import HttpUrl

from shared_data_model.meta.base import StrEnum
from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Configuration, Source
from shared_data_model.parameters import (
    URL,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    PrivateToken,
    Severities,
    SingleChoiceParameter,
    StringParameter,
    TestResult,
)


class Lines(StrEnum):
    """Line types that SonarQube can report on."""

    ALL = "all lines"
    CODE = "lines with code"


def violation_entity_attributes(
    include_review_priority=False,
    include_resolution=False,
    include_rationale=False,
    include_status=False,
) -> list[EntityAttribute]:
    """Return the violation entity attributes."""
    attributes = [
        EntityAttribute(name="Message"),
        EntityAttribute(
            name="Severity",
            color={"blocker": Color.NEGATIVE, "critical": Color.NEGATIVE, "major": Color.WARNING},
        ),
    ]
    if include_review_priority:
        attributes.append(
            EntityAttribute(name="Review priority", color={"high": Color.NEGATIVE, "medium": Color.WARNING}),
        )
    attributes.append(EntityAttribute(name="Warning type", key="type"))
    if include_status:
        attributes.append(EntityAttribute(name="Hotspot status"))
    if include_resolution:
        attributes.append(EntityAttribute(name="Resolution"))
    if include_rationale:
        attributes.append(EntityAttribute(name="Rationale"))
    attributes.extend(
        [
            EntityAttribute(name="Component", url="url"),
            EntityAttribute(name="Created", key="creation_date", type=EntityAttributeType.DATETIME),
            EntityAttribute(name="Updated", key="update_date", type=EntityAttributeType.DATETIME),
        ],
    )
    return attributes


PROJECT_METRICS = [
    "commented_out_code",
    "complex_units",
    "duplicated_lines",
    "loc",
    "long_units",
    "many_parameters",
    "remediation_effort",
    "security_warnings",
    "software_version",
    "source_up_to_dateness",
    "suppressed_violations",
    "tests",
    "uncovered_branches",
    "uncovered_lines",
    "violations",
]

ALL_SONARQUBE_METRICS = sorted([*PROJECT_METRICS, "source_version"], key=str)


VIOLATION_ENTITY = Entity(name="violation", attributes=violation_entity_attributes())

SONARQUBE = Source(
    name="SonarQube",
    description="SonarQube is an open-source platform for continuous inspection of code quality to perform automatic "
    "reviews with static analysis of code to detect bugs, code smells, and security vulnerabilities on 20+ programming "
    "languages.",
    url=HttpUrl("https://www.sonarqube.org"),
    configuration={
        "commented_out_rules": Configuration(
            metrics=["commented_out_code"],
            name="Rules used to detect commented out code",
            value=[
                "Web:AvoidCommentedOutCodeCheck",
                "abap:S125",
                "c:CommentedCode",
                "cpp:CommentedCode",
                "csharpsquid:S125",
                "flex:CommentedCode",
                "java:S125",
                "javascript:S125",
                "kotlin:S125",
                "objc:CommentedCode",
                "php:S125",
                "plsql:S125",
                "python:S125",
                "scala:S125",
                "swift:S125",
                "typescript:S125",
                "xml:S125",
            ],
        ),
        "complex_unit_rules": Configuration(
            metrics=["complex_units"],
            name="Rules used to detect complex units",
            value=[
                "csharpsquid:S1541",
                "csharpsquid:S3776",
                "flex:FunctionComplexity",
                "go:S3776",
                "java:S1541",
                "java:S3776",
                "javascript:S1541",
                "javascript:S3776",
                "kotlin:S3776",
                "php:S1541",
                "php:S3776",
                "python:FunctionComplexity",
                "python:S3776",
                "ruby:S3776",
                "scala:S3776",
                "swift:S1541",
                "typescript:S1541",
                "typescript:S3776",
                "vbnet:S1541",
                "vbnet:S3776",
            ],
        ),
        "many_parameter_rules": Configuration(
            metrics=["many_parameters"],
            name="Rules used to detect units with many parameters",
            value=[
                "c:S107",
                "cpp:S107",
                "csharpsquid:S107",
                "csharpsquid:S2436",
                "flex:S107",
                "java:S107",
                "javascript:S107",
                "kotlin:S107",
                "objc:S107",
                "php:S107",
                "python:S107",
                "swift:S107",
                "tsql:S107",
                "typescript:S107",
            ],
        ),
        "long_unit_rules": Configuration(
            metrics=["long_units"],
            name="Rules used to detect long units",
            value=[
                "Pylint:R0915",
                "Web:FileLengthCheck",
                "Web:LongJavaScriptCheck",
                "abap:S104",
                "c:FileLoc",
                "cpp:FileLoc",
                "csharpsquid:S104",
                "csharpsquid:S138",
                "flex:S138",
                "go:S104",
                "go:S138",
                "java:S104",
                "java:S1188",
                "java:S138",
                "java:S2972",
                "javascript:S104",
                "javascript:S138",
                "kotlin:S104",
                "kotlin:S138",
                "objc:FileLoc",
                "php:S104",
                "php:S138",
                "php:S2042",
                "python:S104",
                "python:S138",
                "ruby:S104",
                "ruby:S138",
                "scala:S104",
                "scala:S138",
                "swift:S104",
                "swift:S138",
                "typescript:S104",
                "typescript:S138",
                "vbnet:S104",
                "vbnet:S138",
            ],
        ),
        "suppression_rules": Configuration(
            metrics=["suppressed_violations"],
            name="Rules used to detect suppressed violations",
            value=[
                "Pylint:I0011",
                "Pylint:I0020",
                "csharpsquid:S1309",
                "java:NoSonar",
                "java:S1309",
                "java:S1310",
                "java:S1315",
                "php:NoSonar",
                "python:NoSonar",
            ],
        ),
    },
    parameters={
        "url": URL(
            name="URL",
            help="URL of the SonarQube instance, with port if necessary, but without path. For example, "
            "'https://sonarcloud.io'.",
            validate_on=["private_token"],
            metrics=ALL_SONARQUBE_METRICS,
        ),
        "private_token": PrivateToken(
            help_url=HttpUrl("https://docs.sonarqube.org/latest/user-guide/user-token/"),
            metrics=ALL_SONARQUBE_METRICS,
        ),
        "component": StringParameter(
            name="Project key",
            help="The project key can be found by opening the project in SonarQube and looking at the bottom of "
            "the grey column on the right.",
            mandatory=True,
            metrics=PROJECT_METRICS,
        ),
        "branch": StringParameter(
            name="Branch (only supported by commercial SonarQube editions)",
            short_name="branch",
            help_url=HttpUrl("https://docs.sonarqube.org/latest/branches/overview/"),
            default_value="master",
            metrics=PROJECT_METRICS,
        ),
        "languages_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Languages to ignore (regular expressions or language names)",
            short_name="languages to ignore",
            help_url=HttpUrl("https://docs.sonarqube.org/latest/analysis/languages/overview/"),
            metrics=["loc"],
        ),
        "lines_to_count": SingleChoiceParameter(
            name="Lines to count",
            help="Either count all lines including lines with comments or only count lines with code, excluding "
            "comments. Note: it's possible to ignore specific languages only when counting lines with code. "
            "This is a SonarQube limitation.",
            default_value=Lines.CODE,
            values=[Lines.ALL, Lines.CODE],
            api_values={Lines.ALL: "lines", Lines.CODE: "ncloc"},
            metrics=["loc"],
        ),
        "test_result": TestResult(values=["errored", "failed", "passed", "skipped"]),
        "severities": Severities(
            help_url=HttpUrl("https://docs.sonarqube.org/latest/user-guide/issues/"),
            values=["info", "minor", "major", "critical", "blocker"],
            metrics=["security_warnings", "suppressed_violations", "violations"],
        ),
        "hotspot_statuses": MultipleChoiceParameter(
            name="Security hotspot statuses",
            short_name="hotspot statuses",
            help_url=HttpUrl("https://docs.sonarqube.org/latest/user-guide/security-hotspots/"),
            placeholder="all hotspot statuses",
            values=["to review", "acknowledged", "safe", "fixed"],
            default_value=["to review", "acknowledged"],
            metrics=["security_warnings"],
        ),
        "review_priorities": MultipleChoiceParameter(
            name="Security hotspot review priorities",
            short_name="review priorities",
            help_url=HttpUrl("https://docs.sonarqube.org/latest/user-guide/security-hotspots/"),
            placeholder="all review priorities",
            values=["low", "medium", "high"],
            metrics=["security_warnings"],
        ),
        "effort_types": MultipleChoiceParameter(
            name="Types of effort",
            short_name="effort types",
            placeholder="all effort types",
            help_url=HttpUrl("https://docs.sonarqube.org/latest/user-guide/metric-definitions/"),
            values=[
                "effort to fix all code smells",
                "effort to fix all bug issues",
                "effort to fix all vulnerabilities",
            ],
            api_values={
                "effort to fix all code smells": "sqale_index",
                "effort to fix all bug issues": "reliability_remediation_effort",
                "effort to fix all vulnerabilities": "security_remediation_effort",
            },
            metrics=["remediation_effort"],
        ),
        "types": MultipleChoiceParameter(
            name="Types",
            placeholder="all violation types",
            help_url=HttpUrl("https://docs.sonarqube.org/latest/user-guide/rules/"),
            values=["code_smell", "bug", "vulnerability"],
            metrics=["suppressed_violations", "violations"],
        ),
        "security_types": MultipleChoiceParameter(
            name="Security issue types (measuring security hotspots requires SonarQube 8.2 or newer)",
            short_name="types",
            placeholder="vulnerability",
            help_url=HttpUrl("https://docs.sonarqube.org/latest/user-guide/rules/"),
            default_value=["vulnerability"],
            values=["security_hotspot", "vulnerability"],
            metrics=["security_warnings"],
        ),
    },
    entities={
        "commented_out_code": VIOLATION_ENTITY,
        "complex_units": VIOLATION_ENTITY,
        "many_parameters": VIOLATION_ENTITY,
        "loc": Entity(
            name="language",
            measured_attribute="ncloc",
            attributes=[
                EntityAttribute(name="Language"),
                EntityAttribute(name="Number of lines with code", key="ncloc", type=EntityAttributeType.INTEGER),
            ],
        ),
        "long_units": VIOLATION_ENTITY,
        "remediation_effort": Entity(
            name="effort type",
            measured_attribute="effort",
            attributes=[
                EntityAttribute(name="Effort type", url="url"),
                EntityAttribute(name="Effort (minutes)", key="effort", type=EntityAttributeType.INTEGER),
            ],
        ),
        "security_warnings": Entity(
            name="security warning",
            attributes=violation_entity_attributes(include_review_priority=True, include_status=True),
        ),
        "suppressed_violations": Entity(
            name="violation",
            attributes=violation_entity_attributes(include_resolution=True, include_rationale=True),
        ),
        "violations": Entity(name="violation", attributes=violation_entity_attributes()),
    },
)
