"""Harbor source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    FixAvailability,
    MultipleChoiceWithAdditionParameter,
    Severities,
    StringParameter,
    access_parameters,
)

ALL_HARBOR_METRICS = ["security_warnings"]
HARBOR_URL = HttpUrl("https://goharbor.io")
HARBOR_DESCRIPTION = (
    "Harbor is an open source registry that secures artifacts with policies and role-based access control, "
    "ensures images are scanned and free from vulnerabilities, and signs images as trusted."
)

HARBOR = Source(
    name="Harbor",
    description=HARBOR_DESCRIPTION,
    url=HARBOR_URL,
    parameters={
        "projects_to_include": MultipleChoiceWithAdditionParameter(
            name="Projects to include (regular expressions or project names)",
            help="Projects to include can be specified by project name or by regular expression.",
            placeholder="all",
            metrics=["security_warnings"],
        ),
        "projects_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Projects to ignore (regular expressions or project names)",
            help="Projects to ignore can be specified by project name or by regular expression.",
            placeholder="none",
            metrics=["security_warnings"],
        ),
        "repositories_to_include": MultipleChoiceWithAdditionParameter(
            name="Repositories to include (regular expressions or repository names)",
            help="Repositories to include can be specified by repository name or by regular expression.",
            placeholder="all",
            metrics=["security_warnings"],
        ),
        "repositories_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Repositories to ignore (regular expressions or repository names)",
            help="Repositories to ignore can be specified by repository name or by regular expression.",
            placeholder="none",
            metrics=["security_warnings"],
        ),
        "severities": Severities(values=["unknown", "low", "medium", "high", "critical"]),
        "fix_availability": FixAvailability(),
        "robot_account_prefix": StringParameter(
            name="Robot account prefix",
            help_url=HttpUrl(
                "https://goharbor.io/docs/2.3.0/administration/robot-accounts/#configure-robot-account-prefix"
            ),
            default_value="robot",
            mandatory=True,
            placeholder="robot account prefix",
            metrics=["security_warnings"],
        ),
        **access_parameters(
            ALL_HARBOR_METRICS,
            include={"private_token": False, "landing_url": False},  # nosec
            kwargs={
                "url": {
                    "help": "URL of the Harbor instance, with port if necessary, but without path. For example "
                    "'https://demo.goharbor.io'.",
                },
            },
        ),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            measured_attribute="total",
            attributes=[
                EntityAttribute(name="Project"),
                EntityAttribute(name="Repository"),
                EntityAttribute(name="Tags"),
                EntityAttribute(name="Artifact", url="url"),
                EntityAttribute(name="Highest severity", color={"Critical": Color.NEGATIVE, "High": Color.WARNING}),
                EntityAttribute(name="Fixable", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Total", type=EntityAttributeType.INTEGER),
            ],
        ),
    },
)

ALL_HARBOR_JSON_METRICS = ["security_warnings", "source_up_to_dateness"]

HARBOR_JSON = Source(
    name="Harbor JSON",
    description=(
        HARBOR_DESCRIPTION + " Use Harbor JSON as source for accessing vulnerability reports downloaded from "
        "the Harbor API in JSON format."
    ),
    url=HARBOR_URL,
    parameters={
        "severities": Severities(values=["unknown", "low", "medium", "high", "critical"]),
        "fix_availability": FixAvailability(),
        **access_parameters(
            ALL_HARBOR_JSON_METRICS,
            source_type="Harbor vulnerability report",
            source_type_format="JSON",
        ),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Vulnerability id", url="url"),
                EntityAttribute(name="Package"),
                EntityAttribute(name="Version"),
                EntityAttribute(name="Fix version"),
                EntityAttribute(name="Severity", color={"Critical": Color.NEGATIVE, "High": Color.WARNING}),
                EntityAttribute(name="Description"),
            ],
        ),
    },
)
