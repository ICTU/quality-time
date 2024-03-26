"""Dependency-Track source."""

from pydantic import HttpUrl

from shared_data_model.meta.parameter import ParameterGroup
from shared_data_model.meta.source import Source
from shared_data_model.parameters import URL, LandingURL

ALL_DEPENDENCY_TRACK_METRICS = ["source_version"]
DEPENDENCY_TRACK_URL = HttpUrl("https://dependencytrack.org")
DEPENDENCY_TRACK_DESCRIPTIlON = (
    "Dependency-Track is an intelligent Component Analysis platform that allows organizations to identify and "
    "reduce risk in the software supply chain."
)

DEPENDENCY_TRACK = Source(
    name="Dependency-Track",
    description=DEPENDENCY_TRACK_DESCRIPTIlON,
    url=DEPENDENCY_TRACK_URL,
    parameters={
        "url": URL(
            name="URL of the Dependency-Track API",
            help="URL of the Dependency-Track API, with port if necessary, but without path. For example, "
            "'https://dependencytrack.example.org'.",
            metrics=ALL_DEPENDENCY_TRACK_METRICS,
            validate_on=[],
        ),
        "landing_url": LandingURL(
            name="URL of the Dependency-Track instance",
            help="URL of the Dependency-Track instance, with port if necessary, but without path. For example, "
            "'https://dependencytrack.example.org'. If provided, users clicking the source URL will visit this URL "
            "instead of the Dependency-Track API.",
            metrics=ALL_DEPENDENCY_TRACK_METRICS,
        ),
    },
    parameter_layout={
        "location": ParameterGroup(name="Source location"),
    },
)
