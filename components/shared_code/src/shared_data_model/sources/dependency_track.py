"""Dependency-Track source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    GitHubPersonalAccessToken,
    LandingURL,
    MultipleChoiceWithAdditionParameter,
    MultipleChoiceWithDefaultsParameter,
    MultipleChoiceWithoutDefaultsParameter,
    PrivateToken,
    Severities,
    SingleChoiceParameter,
)

ALL_DEPENDENCY_TRACK_METRICS = [
    "dependencies",
    "licenses",
    "security_warnings",
    "source_up_to_dateness",
    "source_version",
]
DEPENDENCY_TRACK_URL = HttpUrl("https://dependencytrack.org")
DEPENDENCY_TRACK_DESCRIPTION = (
    "Dependency-Track is a component analysis platform that allows organizations to identify and "
    "reduce risk in the software supply chain."
)
PROJECT_ATTRIBUTES = [
    EntityAttribute(name="Project", url="project_landing_url"),
    EntityAttribute(name="Project version"),
]
COMPONENT_ATTRIBUTES = [
    EntityAttribute(name="Component", url="component_landing_url"),
    EntityAttribute(
        name="Root component",
        url="root_component_landing_url",
        help="The direct dependency of the project through which this component is included. Empty if the project "
        "depends on this component directly. If the component is included through more than one dependency, all of "
        "them are listed.",
    ),
]
LICENSE_GROUPS = ["Copyleft", "Weak Copyleft", "Permissive", "Non-Commercial"]  # Dependency-Track's default groups
LICENSE_ATTRIBUTES = ["OSI-approved", "FSF-Libre", "Deprecated"]
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
    repository_url=HttpUrl("https://github.com/DependencyTrack/dependency-track"),
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
            "'https://www.dependencytrack.example.org'.",
            mandatory=True,
            metrics=ALL_DEPENDENCY_TRACK_METRICS,
        ),
        "private_token": PrivateToken(
            name="API key (with view_portfolio and view_vulnerability permissions)",
            help_url=HttpUrl("https://docs.dependencytrack.org/integrations/rest-api/"),
            metrics=["dependencies", "licenses", "source_up_to_dateness", "security_warnings"],
        ),
        "project_names": MultipleChoiceWithAdditionParameter(
            name="Project names (regular expressions or project names)",
            placeholder="all project names",
            metrics=["dependencies", "licenses", "security_warnings", "source_up_to_dateness"],
        ),
        "project_versions": MultipleChoiceWithAdditionParameter(
            name="Project versions (regular expressions or versions)",
            placeholder="all project versions",
            metrics=["dependencies", "licenses", "security_warnings", "source_up_to_dateness"],
        ),
        "components_to_include": MultipleChoiceWithAdditionParameter(
            name="Components to include (regular expressions or component names)",
            placeholder="all components",
            metrics=["dependencies", "licenses", "security_warnings"],
        ),
        "components_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Components to ignore (regular expressions or component names)",
            placeholder="none",
            metrics=["dependencies", "licenses", "security_warnings"],
        ),
        "licenses_to_include": MultipleChoiceWithAdditionParameter(
            name="Licenses to include (regular expressions, license names, or SPDX license identifiers)",
            placeholder="all licenses",
            metrics=["licenses"],
        ),
        "licenses_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Licenses to ignore (regular expressions, license names, or SPDX license identifiers)",
            metrics=["licenses"],
        ),
        "license_groups_to_include": MultipleChoiceWithoutDefaultsParameter(
            name="License groups to include",
            help="Only count licenses that belong to at least one of these license groups.",
            placeholder="all license groups",
            values=LICENSE_GROUPS,
            metrics=["licenses"],
        ),
        "license_groups_to_ignore": MultipleChoiceWithoutDefaultsParameter(
            name="License groups to ignore",
            help="Don't count licenses that belong to any of these license groups.",
            values=LICENSE_GROUPS,
            metrics=["licenses"],
        ),
        "license_attributes_to_include": MultipleChoiceWithoutDefaultsParameter(
            name="License attributes to include",
            help="Only count licenses that have at least one of these attributes.",
            placeholder="all license attributes",
            values=LICENSE_ATTRIBUTES,
            metrics=["licenses"],
        ),
        "license_attributes_to_ignore": MultipleChoiceWithoutDefaultsParameter(
            name="License attributes to ignore",
            help="Don't count licenses that have any of these attributes.",
            values=LICENSE_ATTRIBUTES,
            metrics=["licenses"],
        ),
        "latest_version_status": MultipleChoiceWithDefaultsParameter(
            name="Latest version statuses",
            placeholder="all statuses",
            help="Limit which latest version statuses to show.",
            values=["up-to-date", "update possible", "unknown"],
            metrics=["dependencies", "security_warnings"],
        ),
        "severities": Severities(values=["Unassigned", "Info", "Low", "Medium", "High", "Critical"]),
        "project_event_types": MultipleChoiceWithDefaultsParameter(
            name="Project event types",
            placeholder="all event types",
            default_value=["last BOM import"],
            help="Project event types to consider for measuring the up-to-dateness.",
            values=["last BOM analysis", "last BOM import"],
            metrics=["source_up_to_dateness"],
        ),
        "only_include_latest_project_versions": SingleChoiceParameter(
            name="Only include latest project versions",
            values=["yes", "no"],
            default_value="no",
            help="Only include project versions that are marked as latest.",
            metrics=["dependencies", "licenses", "security_warnings", "source_up_to_dateness"],
        ),
        "github_pat": GitHubPersonalAccessToken(metrics=["source_version"]),
    },
    entities={
        "dependencies": Entity(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                *PROJECT_ATTRIBUTES,
                *COMPONENT_ATTRIBUTES,
                *VERSION_ATTRIBUTES,
            ],
        ),
        "licenses": Entity(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                *PROJECT_ATTRIBUTES,
                EntityAttribute(name="Component", url="component_landing_url"),
                EntityAttribute(name="Component version"),
                EntityAttribute(name="License"),
                EntityAttribute(name="License identifier", key="license_id", visible=False),
                EntityAttribute(name="License groups"),
                EntityAttribute(name="License attributes"),
            ],
        ),
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                *PROJECT_ATTRIBUTES,
                *COMPONENT_ATTRIBUTES,
                EntityAttribute(name="Identifier"),
                EntityAttribute(name="Description"),
                EntityAttribute(name="Severity", color={"Critical": Color.NEGATIVE, "High": Color.WARNING}),
                *VERSION_ATTRIBUTES,
            ],
        ),
        "source_up_to_dateness": Entity(
            name="project",
            attributes=[
                *PROJECT_ATTRIBUTES,
                EntityAttribute(name="Latest", key="is_latest", type=EntityAttributeType.BOOLEAN),
                EntityAttribute(name="Last BOM import", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Last BOM analysis", type=EntityAttributeType.DATETIME),
                EntityAttribute(
                    name="Up-to-date",
                    color={
                        "nearly": Color.WARNING,
                        "no": Color.NEGATIVE,
                        "yes": Color.POSITIVE,
                        "unknown": Color.ACTIVE,
                    },
                ),
            ],
        ),
    },
)
