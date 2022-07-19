"""Cloc source."""

from ..meta.entity import EntityAttributeType
from ..meta.source import Source
from ..parameters import access_parameters, MultipleChoiceWithAdditionParameter


ALL_CLOC_METRICS = ["loc", "source_version"]

CLOC = Source(
    name="cloc",
    description="cloc is an open-source tool for counting blank lines, comment lines, and physical lines of source "
    "code in many programming languages.",
    url="https://github.com/AlDanial/cloc",
    parameters=dict(
        languages_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Languages to ignore (regular expressions or language names)",
            short_name="languages to ignore",
            help_url="https://github.com/AlDanial/cloc#recognized-languages-",
            metrics=["loc"],
        ),
        **access_parameters(ALL_CLOC_METRICS, source_type="cloc report", source_type_format="JSON")
    ),
    entities=dict(
        loc=dict(
            name="language",
            measured_attribute="code",
            attributes=[
                dict(name="Language"),
                dict(name="Number of files", key="nr_files", type=EntityAttributeType.INTEGER),
                dict(name="Number of blank lines", key="blank", type=EntityAttributeType.INTEGER),
                dict(name="Number of comment lines", key="comment", type=EntityAttributeType.INTEGER),
                dict(name="Number of code lines", key="code", type=EntityAttributeType.INTEGER),
            ],
        )
    ),
)
