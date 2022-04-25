"""SARIF JSON for security warnings source."""

from ..meta.source import Source
from ..parameters import access_parameters


SARIF_JSON = Source(
    name="SARIF",
    description="A Static Analysis Results Interchange Format (SARIF) vulnerability report in JSON format.",
    url="https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=sarif",
    parameters=dict(
        **access_parameters(["security_warnings"], source_type="SARIF vulnerability report", source_type_format="JSON")
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[
                dict(name="Title", url="url"),
                dict(name="Description"),
            ],
        )
    ),
)
