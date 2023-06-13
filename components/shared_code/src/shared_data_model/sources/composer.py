"""Composer source."""

from shared_data_model.meta.entity import Color
from shared_data_model.meta.source import Source
from shared_data_model.parameters import MultipleChoiceParameter, access_parameters

COMPOSER = Source(
    name="Composer",
    description="A Dependency Manager for PHP.",
    url="https://getcomposer.org/",
    parameters=dict(
        latest_version_status=MultipleChoiceParameter(
            name="Latest version statuses",
            short_name="statuses",
            placeholder="all statuses",
            help="Limit which latest version statuses to show. The status 'safe update possible' means that based on "
            "semantic versioning the update should be backwards compatible.",
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
            kwargs={"url": {"help_url": "https://getcomposer.org/doc/03-cli.md#outdated"}},
        ),
    ),
    entities={
        "dependencies": {
            "name": "dependency",
            "name_plural": "dependencies",
            "attributes": [
                {"name": "Package", "key": "name", "url": "homepage"},
                {"name": "Description"},
                {"name": "Current version", "key": "version"},
                {"name": "Latest version", "key": "latest"},
                {
                    "name": "Latest version status",
                    "key": "latest_status",
                    "color": {
                        "up-to-date": Color.POSITIVE,
                        "semver-safe-update": Color.WARNING,
                        "update-possible": Color.NEGATIVE,
                    },
                },
                {"name": "Warning"},
            ],
        },
    },
)
