"""Dependency-Track source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    LandingURL,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    PrivateToken,
    Severities,
)

ALL_DEPENDENCY_TRACK_METRICS = ["dependencies", "security_warnings", "source_up_to_dateness", "source_version"]
DEPENDENCY_TRACK_URL = HttpUrl("https://dependencytrack.org")
DEPENDENCY_TRACK_DESCRIPTION = (
    "Dependency-Track is a component analysis platform that allows organizations to identify and "
    "reduce risk in the software supply chain."
)
VERSION_ATTRIBUTES = [
    EntityAttribute(name="Current version", key="version"),
    EntityAttribute(name="Latest version", key="latest"),
    EntityAttribute(
        name="Latest version status",
        key="latest_version_status",
        color={
            "unknown": Color.ACTIVE,
            "up-to-date": Color.POSITIVE,
            "update possible": Color.WARNING,
        },
    ),
]

DEPENDENCY_TRACK = Source(
    name="Dependency-Track",
    description=DEPENDENCY_TRACK_DESCRIPTION,
    url=DEPENDENCY_TRACK_URL,
    parameters={
        "url": URL(
            name="URL of the Dependency-Track API",
            help="URL of the Dependency-Track API, with port if necessary, but without path. For example, "
            "'https://api.dependencytrack.example.org'.",
            metrics=ALL_DEPENDENCY_TRACK_METRICS,
            validate_on=["private_token"],
        ),
        "landing_url": LandingURL(
            name="URL of the Dependency-Track instance",
            help="URL of the Dependency-Track instance, with port if necessary, but without path. For example, "
            "'https://www.dependencytrack.example.org'. If provided, users clicking the source URL will visit this URL "
            "instead of the Dependency-Track API.",
            metrics=ALL_DEPENDENCY_TRACK_METRICS,
        ),
        "private_token": PrivateToken(
            name="API key",
            help_url=HttpUrl("https://docs.dependencytrack.org/integrations/rest-api/"),
            metrics=["dependencies", "source_up_to_dateness", "security_warnings"],
        ),
        "project_names": MultipleChoiceWithAdditionParameter(
            name="Project names (regular expressions or project names)",
            placeholder="all project names",
            short_name="project names",
            metrics=["dependencies", "security_warnings", "source_up_to_dateness"],
        ),
        "project_versions": MultipleChoiceWithAdditionParameter(
            name="Project versions (regular expressions or versions)",
            placeholder="all project versions",
            short_name="project versions",
            metrics=["dependencies", "security_warnings", "source_up_to_dateness"],
        ),
        "components_to_include": MultipleChoiceWithAdditionParameter(
            name="Components to include (regular expressions or component names)",
            placeholder="all components",
            short_name="components to include",
            metrics=["dependencies", "security_warnings"],
        ),
        "components_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Components to ignore (regular expressions or component names)",
            placeholder="none",
            short_name="components to ignore",
            metrics=["dependencies", "security_warnings"],
        ),
        "latest_version_status": MultipleChoiceParameter(
            name="Latest version statuses",
            short_name="statuses",
            placeholder="all statuses",
            help="Limit which latest version statuses to show.",
            values=["up-to-date", "update possible", "unknown"],
            metrics=["dependencies", "security_warnings"],
        ),
        "severities": Severities(values=["Unassigned", "Info", "Low", "Medium", "High", "Critical"]),
        "project_event_types": MultipleChoiceParameter(
            name="Project event types",
            short_name="event types",
            placeholder="all event types",
            default_value=["last BOM import"],
            help="Project event types to consider for measuring the up-to-dateness.",
            values=["last BOM analysis", "last BOM import"],
            metrics=["source_up_to_dateness"],
        ),
    },
    entities={
        "dependencies": Entity(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                EntityAttribute(name="Project", url="project_landing_url"),
                EntityAttribute(name="Component", url="component_landing_url"),
                *VERSION_ATTRIBUTES,
            ],
        ),
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Project", url="project_landing_url"),
                EntityAttribute(name="Component", url="component_landing_url"),
                EntityAttribute(name="Identifier"),
                EntityAttribute(name="Description"),
                EntityAttribute(name="Severity", color={"Critical": Color.NEGATIVE, "High": Color.WARNING}),
                *VERSION_ATTRIBUTES,
            ],
        ),
        "source_up_to_dateness": Entity(
            name="project",
            attributes=[
                EntityAttribute(name="Project", url="project_landing_url"),
                EntityAttribute(name="Last BOM import", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Last BOM analysis", type=EntityAttributeType.DATETIME),
            ],
        ),
    },
)
