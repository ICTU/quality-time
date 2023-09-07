"""Composer source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import MultipleChoiceParameter, access_parameters

COMPOSER = Source(
    name="Composer",
    description="A Dependency Manager for PHP.",
    url=HttpUrl("https://getcomposer.org/"),
    parameters={
        "latest_version_status": MultipleChoiceParameter(
            name="Latest version statuses",
            short_name="statuses",
            placeholder="all statuses",
            help="Limit which latest version statuses to show. The status 'safe update possible' means that based "
            "on semantic versioning the update should be backwards compatible.",
            values=["safe update possible", "up-to-date", "update possible", "unknown"],
            api_values={
                "safe update possible": "semver-safe-update",
                "unknown": "unknown",
                "up-to-date": "up-to-date",
                "update possible": "update-possible",
            },
            metrics=["dependencies"],
        ),
        **access_parameters(
            ["dependencies"],
            source_type="Composer 'outdated' report",
            source_type_format="JSON",
            kwargs={"url": {"help_url": HttpUrl("https://getcomposer.org/doc/03-cli.md#outdated")}},
        ),
    },
    entities={
        "dependencies": Entity(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                EntityAttribute(name="Package", key="name", url="homepage"),
                EntityAttribute(name="Description"),
                EntityAttribute(name="Current version", key="version"),
                EntityAttribute(name="Latest version", key="latest"),
                EntityAttribute(
                    name="Latest version status",
                    key="latest_status",
                    color={
                        "up-to-date": Color.POSITIVE,
                        "semver-safe-update": Color.WARNING,
                        "update-possible": Color.NEGATIVE,
                    },
                ),
                EntityAttribute(name="Warning"),
            ],
        ),
    },
)
