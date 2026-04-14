"""Manual version source."""

from shared_data_model.meta.parameter import ParameterGroup
from shared_data_model.meta.source import Source
from shared_data_model.meta.unit import Unit
from shared_data_model.parameters import StringParameter

MANUAL_VERSION = Source(
    name="Manual version",
    description="A version entered manually by a Quality-time user.",
    documentation={
        "generic": """The manual version source supports all metric types that take a version as value.
Because users have to keep the value up to date by hand, this source is only meant to be used as a temporary
solution for when no automated source is available yet. For example, when the source version of a tool cannot be
measured by Quality-time (yet).""",
    },
    parameters={
        "version": StringParameter(
            name="Version",
            mandatory=True,
            unit=Unit.NONE,
            metrics=[
                "software_version",
                "source_version",
            ],
        ),
    },
    parameter_layout={
        "version": ParameterGroup(name="Manual source data"),
    },
)
