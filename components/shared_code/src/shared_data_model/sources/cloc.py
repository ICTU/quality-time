"""Cloc source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import MultipleChoiceWithAdditionParameter, access_parameters

ALL_CLOC_METRICS = ["loc", "source_version"]

CLOC = Source(
    name="cloc",
    description="cloc is an open-source tool for counting blank lines, comment lines, and physical lines of source "
    "code in many programming languages.",
    url=HttpUrl("https://github.com/AlDanial/cloc"),
    parameters={
        "languages_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Languages to ignore (regular expressions or language names)",
            short_name="languages to ignore",
            help_url=HttpUrl("https://github.com/AlDanial/cloc#recognized-languages-"),
            metrics=["loc"],
        ),
        "files_to_include": MultipleChoiceWithAdditionParameter(
            name="Files to include (regular expressions or file names)",
            short_name="files to include",
            help="Note that filtering files only works when the cloc report is generated with the --by-file option.",
            placeholder="all",
            metrics=["loc"],
        ),
        **access_parameters(ALL_CLOC_METRICS, source_type="cloc report", source_type_format="JSON"),
    },
    entities={
        "loc": Entity(
            name="language",
            measured_attribute="code",
            attributes=[
                EntityAttribute(name="Language"),
                EntityAttribute(name="Number of files", key="nr_files", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Number of blank lines", key="blank", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Number of comment lines", key="comment", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Number of code lines", key="code", type=EntityAttributeType.INTEGER),
                EntityAttribute(
                    name="Percentage of code lines", key="code_percentage", type=EntityAttributeType.INTEGER_PERCENTAGE
                ),
            ],
        ),
    },
)
