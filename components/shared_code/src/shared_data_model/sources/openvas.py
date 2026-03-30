"""OpenVAS source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import GitHubPersonalAccessToken, Severities, access_parameters

ALL_OPENVAS_METRICS = ["security_warnings", "source_up_to_dateness", "source_version"]

OPENVAS = Source(
    name="OpenVAS",
    description="OpenVAS (Open Vulnerability Assessment System) is a software framework of several services and tools "
    "offering vulnerability scanning and vulnerability management.",
    url=HttpUrl("https://www.openvas.org"),
    repository_url=HttpUrl("https://github.com/greenbone/openvas-scanner"),
    parameters={
        "severities": Severities(values=["log", "low", "medium", "high"]),
        "github_pat": GitHubPersonalAccessToken(metrics=["source_version"]),
        **access_parameters(ALL_OPENVAS_METRICS, source_type="an OpenVAS report", source_type_format="XML"),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Warning", key="name"),
                EntityAttribute(name="Severity", color={"High": Color.NEGATIVE, "Medium": Color.WARNING}),
                EntityAttribute(name="Description", pre=True),
                EntityAttribute(name="Host"),
                EntityAttribute(name="Port"),
            ],
        ),
    },
)
