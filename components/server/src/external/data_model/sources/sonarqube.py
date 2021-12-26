"""SonarQube source."""

from enum import Enum

from ..meta.entity import Color, EntityAttributeType
from ..meta.source import Source
from ..parameters import (
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    PrivateToken,
    Severities,
    SingleChoiceParameter,
    StringParameter,
    TestResult,
    URL,
)


class Lines(str, Enum):
    """Line types that SonarQube can report on."""

    ALL = "all lines"
    CODE = "lines with code"


def violation_entity_attributes(include_review_priority=False, include_resolution=False):
    """Return the violation entity attributes."""
    attributes = [
        dict(name="Message"),
        dict(name="Severity", color=dict(blocker=Color.NEGATIVE, critical=Color.NEGATIVE, major=Color.WARNING)),
    ]
    if include_review_priority:
        attributes.append(dict(name="Review priority", color=dict(high=Color.NEGATIVE, medium=Color.WARNING)))
    attributes.append(dict(name="Type"))
    if include_resolution:
        attributes.append(dict(name="Resolution"))
    attributes.extend(
        [
            dict(name="Component", url="url"),
            dict(name="Created", key="creation_date", type=EntityAttributeType.DATETIME),
            dict(name="Updated", key="update_date", type=EntityAttributeType.DATETIME),
        ]
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
    "source_up_to_dateness",
    "suppressed_violations",
    "tests",
    "uncovered_branches",
    "uncovered_lines",
    "violations",
]

ALL_SONARQUBE_METRICS = sorted(PROJECT_METRICS + ["source_version"], key=str)


VIOLATION_ENTITY = dict(name="violation", attributes=violation_entity_attributes())

SONARQUBE = Source.parse_obj(
    dict(
        name="SonarQube",
        description="SonarQube is an open-source platform for continuous inspection of code quality to perform "
        "automatic reviews with static analysis of code to detect bugs, code smells, and security "
        "vulnerabilities on 20+ programming languages.",
        url="https://www.sonarqube.org",
        configuration=dict(
            commented_out_rules=dict(
                metrics=["commented_out_code"],
                name="Rules used to detect commented out code",
                value=[
                    "abap:S125",
                    "apex:S125",
                    "c:CommentedCode",
                    "cpp:CommentedCode",
                    "flex:CommentedCode",
                    "csharpsquid:S125",
                    "javascript:CommentedCode",
                    "javascript:S125",
                    "kotlin:S125",
                    "objc:CommentedCode",
                    "php:S125",
                    "plsql:S125",
                    "python:S125",
                    "scala:S125",
                    "squid:CommentedOutCodeLine",
                    "java:S125",
                    "swift:S125",
                    "typescript:S125",
                    "Web:AvoidCommentedOutCodeCheck",
                    "xml:S125",
                ],
            ),
            complex_unit_rules=dict(
                metrics=["complex_units"],
                name="Rules used to detect complex units",
                value=[
                    "csharpsquid:S1541",
                    "csharpsquid:S3776",
                    "flex:FunctionComplexity",
                    "javascript:FunctionComplexity",
                    "javascript:S1541",
                    "javascript:S3776",
                    "go:S3776",
                    "kotlin:S3776",
                    "php:S1541",
                    "php:S3776",
                    "python:FunctionComplexity",
                    "python:S3776",
                    "ruby:S3776",
                    "scala:S3776",
                    "squid:MethodCyclomaticComplexity",
                    "java:S1541",
                    "squid:S3776",
                    "typescript:S1541",
                    "typescript:S3776",
                    "vbnet:S1541",
                    "vbnet:S3776",
                ],
            ),
            many_parameter_rules=dict(
                metrics=["many_parameters"],
                name="Rules used to detect units with many parameters",
                value=[
                    "c:S107",
                    "csharpsquid:S107",
                    "csharpsquid:S2436",
                    "cpp:S107",
                    "flex:S107",
                    "javascript:ExcessiveParameterList",
                    "javascript:S107",
                    "objc:S107",
                    "php:S107",
                    "plsql:PlSql.FunctionAndProcedureExcessiveParameters",
                    "python:S107",
                    "squid:S00107",
                    "java:S107",
                    "tsql:S107",
                    "typescript:S107",
                ],
            ),
            long_unit_rules=dict(
                metrics=["long_units"],
                name="Rules used to detect long units",
                value=[
                    "abap:S104",
                    "c:FileLoc",
                    "cpp:FileLoc",
                    "csharpsquid:S104",
                    "csharpsquid:S138",
                    "flex:S138",
                    "go:S104",
                    "go:S138",
                    "javascript:S104",
                    "javascript:S138",
                    "kotlin:S104",
                    "kotlin:S138",
                    "objc:FileLoc",
                    "php:S104",
                    "php:S138",
                    "php:S2042",
                    "Pylint:R0915",
                    "python:S104",
                    "ruby:S104",
                    "ruby:S138",
                    "scala:S104",
                    "scala:S138",
                    "squid:S00104",
                    "squid:S1188",
                    "squid:S138",
                    "java:S138",
                    "squid:S2972",
                    "swift:S104",
                    "typescript:S104",
                    "typescript:S138",
                    "vbnet:S104",
                    "vbnet:S138",
                    "Web:FileLengthCheck",
                    "Web:LongJavaScriptCheck",
                ],
            ),
            suppression_rules=dict(
                metrics=["suppressed_violations"],
                name="Rules used to detect suppressed violations",
                value=[
                    "csharpsquid:S1309",
                    "php:NoSonar",
                    "Pylint:I0011",
                    "Pylint:I0020",
                    "squid:NoSonar",
                    "java:NoSonar",
                    "squid:S1309",
                    "java:S1309",
                    "squid:S1310",
                    "java:S1310",
                    "squid:S1315",
                    "java:S1315",
                ],
            ),
        ),
        parameters=dict(
            url=URL(
                name="URL",
                help="URL of the SonarQube instance, with port if necessary, but without path. For example, "
                "'https://sonarcloud.io'.",
                validate_on=["private_token"],
                metrics=ALL_SONARQUBE_METRICS,
            ),
            private_token=PrivateToken(
                help_url="https://docs.sonarqube.org/latest/user-guide/user-token/", metrics=ALL_SONARQUBE_METRICS
            ),
            component=StringParameter(
                name="Project key",
                help="The project key can be found by opening the project in SonarQube and looking at the bottom of "
                "the grey column on the right.",
                mandatory=True,
                metrics=PROJECT_METRICS,
            ),
            branch=StringParameter(
                name="Branch (only supported by commercial SonarQube editions)",
                short_name="branch",
                help_url="https://docs.sonarqube.org/latest/branches/overview/",
                default_value="master",
                metrics=PROJECT_METRICS,
            ),
            languages_to_ignore=MultipleChoiceWithAdditionParameter(
                name="Languages to ignore (regular expressions or language names)",
                short_name="languages to ignore",
                help_url="https://docs.sonarqube.org/latest/analysis/languages/overview/",
                metrics=["loc"],
            ),
            lines_to_count=SingleChoiceParameter(
                name="Lines to count",
                help="Either count all lines including lines with comments or only count lines with code, excluding "
                "comments. Note: it's possible to ignore specific languages only when counting lines with code. "
                "This is a SonarQube limitation.",
                default_value=Lines.CODE,
                values=[Lines.ALL, Lines.CODE],
                api_values={Lines.ALL: "lines", Lines.CODE: "ncloc"},
                metrics=["loc"],
            ),
            test_result=TestResult(values=["errored", "failed", "passed", "skipped"]),
            severities=Severities(
                help_url="https://docs.sonarqube.org/latest/user-guide/issues/",
                values=["info", "minor", "major", "critical", "blocker"],
                metrics=["security_warnings", "suppressed_violations", "violations"],
            ),
            review_priorities=MultipleChoiceParameter(
                name="Security hotspot review priorities",
                short_name="review priorities",
                help_url="https://docs.sonarqube.org/latest/user-guide/security-hotspots/",
                placeholder="all review priorities",
                values=["low", "medium", "high"],
                metrics=["security_warnings"],
            ),
            effort_types=MultipleChoiceParameter(
                name="Types of effort",
                short_name="effort types",
                placeholder="all effort types",
                help_url="https://docs.sonarqube.org/latest/user-guide/metric-definitions/",
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
            types=MultipleChoiceParameter(
                name="Types",
                placeholder="all violation types",
                help_url="https://docs.sonarqube.org/latest/user-guide/rules/",
                values=["code_smell", "bug", "vulnerability"],
                metrics=["suppressed_violations", "violations"],
            ),
            security_types=MultipleChoiceParameter(
                name="Security issue types (measuring security hotspots requires SonarQube 8.2 or newer)",
                short_name="types",
                placeholder="all security issue types",
                help_url="https://docs.sonarqube.org/latest/user-guide/rules/",
                default_value=["vulnerability"],
                values=["vulnerability", "security_hotspot"],
                metrics=["security_warnings"],
            ),
        ),
        entities=dict(
            commented_out_code=VIOLATION_ENTITY,
            complex_units=VIOLATION_ENTITY,
            many_parameters=VIOLATION_ENTITY,
            loc=dict(
                name="language",
                measured_attribute="ncloc",
                attributes=[
                    dict(name="Language"),
                    dict(name="Number of lines with code", key="ncloc", type=EntityAttributeType.INTEGER),
                ],
            ),
            long_units=VIOLATION_ENTITY,
            remediation_effort=dict(
                name="effort type",
                measured_attribute="effort",
                attributes=[
                    dict(name="Effort type", url="url"),
                    dict(name="Effort (minutes)", key="effort", type=EntityAttributeType.MINUTES),
                ],
            ),
            security_warnings=dict(
                name="security warning", attributes=violation_entity_attributes(include_review_priority=True)
            ),
            suppressed_violations=dict(
                name="violation", attributes=violation_entity_attributes(include_resolution=True)
            ),
            violations=dict(name="violation", attributes=violation_entity_attributes()),
        ),
    )
)
