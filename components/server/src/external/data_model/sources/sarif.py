"""SARIF JSON for security warnings source."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, Severities


SARIF_JSON = Source(
    name="SARIF",
    description="A Static Analysis Results Interchange Format (SARIF) vulnerability report in JSON format.",
    url="https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=sarif",
    parameters=dict(
        levels=Severities(
            name="Levels",
            placeholder="all levels",
            help="If provided, only count security warnings with the selected levels.",
            values=["none", "note", "warning", "error"],
        ),
        **access_parameters(["security_warnings"], source_type="SARIF vulnerability report", source_type_format="JSON")
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[
                dict(name="Message"),
                dict(name="Level", color=dict(error=Color.NEGATIVE, warning=Color.WARNING, note=Color.ACTIVE)),
                dict(name="Locations"),
                dict(name="Rule", url="url"),
                dict(name="Description"),
            ],
        )
    ),
)
