"""NCover source."""

from ..meta.source import Source
from ..parameters import access_parameters


ALL_NCOVER_METRICS = ["source_up_to_dateness", "uncovered_branches", "uncovered_lines"]

NCOVER = Source(
    name="NCover",
    description="A .NET code coverage solution.",
    url="https://www.ncover.com/",
    parameters=access_parameters(
        ALL_NCOVER_METRICS, source_type="NCover report", source_type_format="HTML", include=dict(landing_url=False)
    ),
)
