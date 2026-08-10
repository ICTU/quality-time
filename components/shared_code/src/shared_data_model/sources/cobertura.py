"""Cobertura source."""

from pydantic import HttpUrl

from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

COBERTURA = Source(
    name="Cobertura",
    description="Cobertura is a free Java tool that calculates the percentage of code accessed by tests.",
    url=HttpUrl("https://cobertura.github.io/cobertura/"),
    parameters=access_parameters(
        [
            "source_up_to_dateness",
            "source_version",
            "uncovered_branches",
            "uncovered_lines",
        ],
        source_type="Cobertura report",
        source_type_format="XML",
    ),
)
