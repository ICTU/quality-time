"""SonarQube source."""

from pydantic import HttpUrl

from shared_data_model.meta.base import StrEnum
from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Configuration, Source
from shared_data_model.parameters import (
    URL,
    MultipleChoiceWithAdditionParameter,
    MultipleChoiceWithDefaultsParameter,
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
    include_security_warning_attributes=False,
    include_suppressed_violation_attributes=False,
) -> list[EntityAttribute]:
    """Return the violation entity attributes."""
    attributes = [
        EntityAttribute(name="Message"),
        EntityAttribute(
            name="Impact",
            key="impacts",
            color={
                "blocker impact on maintainability": Color.NEGATIVE,
                "blocker impact on reliability": Color.NEGATIVE,
                "blocker impact on security": Color.NEGATIVE,
                "high impact on maintainability": Color.NEGATIVE,
                "high impact on reliability": Color.NEGATIVE,
                "high impact on security": Color.NEGATIVE,
                "medium impact on maintainability": Color.WARNING,
                "medium impact on reliability": Color.WARNING,
                "medium impact on security": Color.WARNING,
            },
        ),
        EntityAttribute(name="Clean code attribute", key="clean_code_attribute_category"),
    ]
    if include_security_warning_attributes:
        attributes.append(EntityAttribute(name="Warning type", key="security_type"))
        attributes.append(EntityAttribute(name="Hotspot status"))
        attributes.append(
            EntityAttribute(name="Review priority", color={"high": Color.NEGATIVE, "medium": Color.WARNING}),
        )
    if include_suppressed_violation_attributes:
        attributes.append(EntityAttribute(name="Resolution"))
        attributes.append(EntityAttribute(name="Rationale"))
    attributes.extend(
        [
            EntityAttribute(name="Component", url="url"),
            EntityAttribute(name="Tags"),
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
    "todo_and_fixme_comments",
    "uncovered_branches",
    "uncovered_lines",
    "violations",
]

ALL_SONARQUBE_METRICS = sorted([*PROJECT_METRICS, "source_version"], key=str)

VIOLATION_ENTITY = Entity(name="violation", attributes=violation_entity_attributes())

ISSUE_SECURITY_TYPE = "issue with security impact"

SONARQUBE = Source(
    name="SonarQube",
    description="SonarQube Server is an on-premise analysis tool designed to detect coding issues in 30+ languages, "
    "frameworks, and infrastructure-as-code platforms.",
    supported_versions_description="≥10.2",
    url=HttpUrl("https://www.sonarsource.com/products/sonarqube/"),
    configuration={
        "commented_out_rules": Configuration(
            metrics=["commented_out_code"],
            name="Rules used to detect commented out code",
            value=[
                "Web:AvoidCommentedOutCodeCheck",
                "abap:S125",
                "c:S125",
                "cpp:S125",
                "csharpsquid:S125",
                "css:S125",
                "flex:CommentedCode",
                "java:S125",
                "javascript:S125",
                "kotlin:S125",
                "objc:S125",
                "php:S125",
                "plsql:S125",
                "python:S125",
                "scala:S125",
                "swift:S125",
                "tsql:S125",
                "typescript:S125",
                "xml:S125",
            ],
        ),
        "complex_unit_rules": Configuration(
            metrics=["complex_units"],
            name="Rules used to detect complex units",
            value=[
                "abap:S1541",
                "abap:S3776",
                "c:S1541",
                "c:S3776",
                "cpp:S1541",
                "cpp:S3776",
                "csharpsquid:S1541",
                "csharpsquid:S3776",
                "dart:S1541",
                "dart:S3776",
                "flex:FunctionComplexity",
                "go:S3776",
                "java:S1541",
                "java:S3776",
                "javascript:S1541",
                "javascript:S3776",
                "kotlin:S3776",
                "objc:S1541",
                "objc:S3776",
                "php:S1541",
                "php:S3776",
                "plsql:PlSql.FunctionAndProcedureComplexity",
                "python:FunctionComplexity",
                "python:S3776",
                "ruby:S3776",
                "rust:S3776",
                "scala:S3776",
                "swift:S1541",
                "swift:S3776",
                "typescript:S1541",
                "typescript:S3776",
                "vbnet:S1541",
                "vbnet:S3776",
            ],
        ),
        "long_unit_rules": Configuration(
            metrics=["long_units"],
            name="Rules used to detect long units",
            value=[
                "Web:FileLengthCheck",
                "Web:LongJavaScriptCheck",
                "abap:S104",
                "c:S104",
                "c:S1151",
                "c:S138",
                "cpp:S104",
                "cpp:S1151",
                "cpp:S1188",
                "cpp:S138",
                "cpp:S6184",
                "csharpsquid:S104",
                "csharpsquid:S1151",
                "csharpsquid:S138",
                "flex:S1151",
                "flex:S138",
                "go:S104",
                "go:S1151",
                "go:S138",
                "java:S104",
                "java:S1151",
                "java:S1188",
                "java:S138",
                "java:S2972",
                "java:S5612",
                "javascript:S104",
                "javascript:S138",
                "kotlin:S104",
                "kotlin:S1151",
                "kotlin:S138",
                "kotlin:S5612",
                "objc:S104",
                "objc:S1151",
                "objc:S138",
                "php:S104",
                "php:S1151",
                "php:S138",
                "php:S2042",
                "plsql:S104",
                "plsql:S1151",
                "python:S104",
                "python:S138",
                "ruby:S104",
                "ruby:S1151",
                "ruby:S138",
                "scala:S104",
                "scala:S1151",
                "scala:S138",
                "swift:S104",
                "swift:S1151",
                "swift:S1188",
                "swift:S138",
                "swift:S2042",
                "tsql:S104",
                "tsql:S1151",
                "tsql:S138",
                "typescript:S104",
                "typescript:S138",
                "vbnet:S104",
                "vbnet:S1151",
                "vbnet:S138",
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
                "dart:S107",
                "flex:S107",
                "go:S107",
                "java:S107",
                "javascript:S107",
                "kotlin:S107",
                "objc:S107",
                "php:S107",
                "python:S107",
                "ruby:S107",
                "rust:S107",
                "scala:S107",
                "swift:S107",
                "tsql:S107",
                "typescript:S107",
                "vbnet:S107",
            ],
        ),
        "suppression_rules": Configuration(
            metrics=["suppressed_violations"],
            name="Rules used to detect suppressed violations",
            value=[
                "c:NoSonar",
                "cpp:NoSonar",
                "csharpsquid:S1309",
                "java:NoSonar",
                "java:S1309",
                "java:S1310",
                "java:S1315",
                "javascript:S1291",
                "objc:NoSonar",
                "php:NoSonar",
                "plsql:NoSonarCheck",
                "python:NoSonar",
                "tsql:NoSonar",
                "typescript:S1291",
            ],
        ),
        "todo_and_fixme_comment_rules": Configuration(
            metrics=["todo_and_fixme_comments"],
            name="Rules used to detect todo and fixme comments",
            value=[
                "Web:S1134",
                "Web:S1135",
                "ansible:S1135",
                "c:S1134",
                "c:S1135",
                "cloudformation:S1135",
                "cpp:S1134",
                "cpp:S1135",
                "csharpsquid:S1134",
                "csharpsquid:S1135",
                "dart:S1134",
                "dart:S1135",
                "docker:S1135",
                "go:S1134",
                "go:S1135",
                "java:S1134",
                "java:S1135",
                "javascript:S1134",
                "javascript:S1135",
                "kotlin:S1134",
                "kotlin:S1135",
                "kubernetes:S1135",
                "objc:S1134",
                "objc:S1135",
                "php:S1134",
                "php:S1135",
                "plsql:S1134",
                "plsql:S1135",
                "python:S1134",
                "python:S1135",
                "ruby:S1134",
                "ruby:S1135",
                "scala:S1134",
                "scala:S1135",
                "swift:S1134",
                "swift:S1135",
                "terraform:S1135",
                "tsql:S1134",
                "tsql:S1135",
                "typescript:S1134",
                "typescript:S1135",
                "vbnet:S1134",
                "vbnet:S1135",
                "xml:S1134",
                "xml:S1135",
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
            help_url=HttpUrl("https://docs.sonarsource.com/sonarqube-server/latest/user-guide/managing-tokens/"),
            metrics=ALL_SONARQUBE_METRICS,
        ),
        "component": StringParameter(
            name="Project key",
            help="The project key can be found by opening the project in SonarQube and clicking 'Project Information'.",
            mandatory=True,
            metrics=PROJECT_METRICS,
        ),
        "branch": StringParameter(
            name="Branch (only supported by commercial SonarQube editions)",
            short_name="branch",
            help_url=HttpUrl(
                "https://docs.sonarsource.com/sonarqube-server/latest/analyzing-source-code/branch-analysis/introduction/"
            ),
            default_value="main",
            metrics=PROJECT_METRICS,
        ),
        "languages_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Languages to ignore (regular expressions or language names)",
            short_name="languages to ignore",
            help_url=HttpUrl(
                "https://docs.sonarsource.com/sonarqube-server/latest/analyzing-source-code/languages/overview/"
            ),
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
        "impact_severities": Severities(
            name="Impact severities",
            placeholder="all impact severities",
            help_url=HttpUrl("https://docs.sonarsource.com/sonarqube-server/latest/user-guide/rules/overview/"),
            values=["info", "low", "medium", "high", "blocker"],
            metrics=["security_warnings", "suppressed_violations", "violations"],
        ),
        "impacted_software_qualities": MultipleChoiceWithDefaultsParameter(
            name="Impacted software qualities",
            placeholder="all impacted software qualities",
            help_url=HttpUrl("https://docs.sonarsource.com/sonarqube/latest/user-guide/clean-code/software-qualities/"),
            values=["maintainability", "reliability", "security"],
            metrics=["suppressed_violations", "violations"],
        ),
        "clean_code_attribute_categories": MultipleChoiceWithDefaultsParameter(
            name="Clean code attribute categories",
            placeholder="all clean code attribute categories",
            help_url=HttpUrl(
                "https://docs.sonarsource.com/sonarqube-server/latest/core-concepts/clean-code/definition/"
            ),
            values=["adaptable", "consistent", "intentional", "responsible"],
            metrics=["suppressed_violations", "violations"],
        ),
        "hotspot_statuses": MultipleChoiceWithDefaultsParameter(
            name="Security hotspot statuses",
            short_name="hotspot statuses",
            help_url=HttpUrl("https://docs.sonarsource.com/sonarqube-server/latest/user-guide/security-hotspots/"),
            placeholder="acknowledged, to review",
            values=["to review", "acknowledged", "safe", "fixed"],
            default_value=["to review", "acknowledged"],
            metrics=["security_warnings"],
        ),
        "review_priorities": MultipleChoiceWithDefaultsParameter(
            name="Security hotspot review priorities",
            short_name="review priorities",
            help_url=HttpUrl("https://docs.sonarsource.com/sonarqube-server/latest/user-guide/security-hotspots/"),
            placeholder="all review priorities",
            values=["low", "medium", "high"],
            metrics=["security_warnings"],
        ),
        "effort_types": MultipleChoiceWithDefaultsParameter(
            name="Types of effort",
            short_name="effort types",
            placeholder="all effort types",
            help_url=HttpUrl(
                "https://docs.sonarsource.com/sonarqube-server/latest/user-guide/code-metrics/metrics-definition/"
            ),
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
        "security_types": MultipleChoiceWithDefaultsParameter(
            name="Security issue types",
            placeholder=ISSUE_SECURITY_TYPE,
            help_url=HttpUrl("https://docs.sonarsource.com/sonarqube-server/latest/user-guide/rules/overview/"),
            default_value=[ISSUE_SECURITY_TYPE],
            values=["security hotspot", ISSUE_SECURITY_TYPE],
            metrics=["security_warnings"],
        ),
        "tags": MultipleChoiceWithAdditionParameter(
            name="Tags to include",
            short_name="tags",
            placeholder="all tags",
            help_url=HttpUrl(
                "https://docs.sonarsource.com/sonarqube-server/latest/user-guide/rules/built-in-rule-tags/"
            ),
            metrics=["security_warnings", "violations"],
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
                EntityAttribute(name="Number of lines", key="ncloc", type=EntityAttributeType.INTEGER),
                EntityAttribute(
                    name="Percentage of lines", key="ncloc_percentage", type=EntityAttributeType.INTEGER_PERCENTAGE
                ),
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
            attributes=violation_entity_attributes(include_security_warning_attributes=True),
        ),
        "suppressed_violations": Entity(
            name="violation",
            attributes=violation_entity_attributes(include_suppressed_violation_attributes=True),
        ),
        "todo_and_fixme_comments": VIOLATION_ENTITY,
        "violations": VIOLATION_ENTITY,
    },
)
