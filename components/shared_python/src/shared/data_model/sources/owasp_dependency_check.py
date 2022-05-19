"""OWASP Dependency Check source."""

from ..meta.entity import Color, EntityAttributeType
from ..meta.source import Source
from ..parameters import access_parameters, MultipleChoiceWithAdditionParameter, Severities


ALL_OWASP_DEPENDENCY_CHECK_METRICS = [
    "dependencies",
    "security_warnings",
    "source_up_to_dateness",
    "source_version",
]

DEPENDENCY_ATTRIBUTES: list[object] = [
    dict(name="File path", url="url"),
    dict(name="File path after applying regular expressions", key="file_path_after_regexp"),
    dict(name="File name"),
]
SECURITY_WARNING_ATTRIBUTES = [
    dict(name="Highest severity", color=dict(Critical=Color.NEGATIVE, High=Color.NEGATIVE, Medium=Color.WARNING)),
    dict(name="Number of vulnerabilities", key="nr_vulnerabilities", type=EntityAttributeType.INTEGER),
]

OWASP_DEPENDENCY_CHECK = Source(
    name="OWASP Dependency Check",
    description="Dependency-Check is a utility that identifies project dependencies and checks if there are any known, "
    "publicly disclosed, vulnerabilities.",
    url="https://owasp.org/www-project-dependency-check/",
    parameters=dict(
        severities=Severities(values=["low", "moderate", "medium", "high", "critical"]),
        variable_file_path_regexp=MultipleChoiceWithAdditionParameter(
            name="Parts of file paths to ignore (regular expressions)",
            short_name="parts of file paths to ignore",
            help="Parts of file paths to ignore can be specified by regular expression. The parts of file paths that "
            "match one or more of the regular expressions are removed. If, after applying the regular expressions, "
            "multiple warnings are the same only one is reported.",
            metrics=["dependencies", "security_warnings"],
        ),
        **access_parameters(
            ALL_OWASP_DEPENDENCY_CHECK_METRICS, source_type="an OWASP Dependency Check report", source_type_format="XML"
        )
    ),
    entities=dict(
        security_warnings=dict(name="security warning", attributes=DEPENDENCY_ATTRIBUTES + SECURITY_WARNING_ATTRIBUTES),
        dependencies=dict(name="dependency", name_plural="dependencies", attributes=DEPENDENCY_ATTRIBUTES),
    ),
)
