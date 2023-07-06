"""Harbor source."""

from shared_data_model.meta.entity import Color, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import MultipleChoiceWithAdditionParameter, access_parameters

ALL_HARBOR_METRICS = ["security_warnings"]

HARBOR = Source(
    name="Harbor",
    description="Harbor is an open source registry that secures artifacts with policies and role-based access control, "
    "ensures images are scanned and free from vulnerabilities, and signs images as trusted.",
    url="https://goharbor.io",
    parameters=dict(
        projects_to_include=MultipleChoiceWithAdditionParameter(
            name="Projects to include (regular expressions or project names)",
            short_name="projects to include",
            help="Projects to include can be specified by project name or by regular expression.",
            placeholder="all",
            metrics=["security_warnings"],
        ),
        projects_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Projects to ignore (regular expressions or project names)",
            short_name="projects to ignore",
            help="Projects to ignore can be specified by project name or by regular expression.",
            placeholder="none",
            metrics=["security_warnings"],
        ),
        repositories_to_include=MultipleChoiceWithAdditionParameter(
            name="Repositories to include (regular expressions or repository names)",
            short_name="repositories to include",
            help="Repositories to include can be specified by repository name or by regular expression.",
            placeholder="all",
            metrics=["security_warnings"],
        ),
        repositories_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Repositories to ignore (regular expressions or repository names)",
            short_name="repositories to ignore",
            help="Repositories to ignore can be specified by repository name or by regular expression.",
            placeholder="none",
            metrics=["security_warnings"],
        ),
        **access_parameters(
            ALL_HARBOR_METRICS,
            include={"private_token": False, "landing_url": False},
            kwargs={
                "url": {
                    "help": "URL of the Harbor instance, with port if necessary, but without path. For example "
                    "'https://demo.goharbor.io'.",
                },
            },
        ),
    ),
    entities={
        "security_warnings": {
            "name": "security warning",
            "measured_attribute": "total",
            "attributes": [
                {"name": "Project"},
                {"name": "Repository"},
                {"name": "Tags"},
                {"name": "Artifact", "url": "url"},
                {"name": "Highest severity", "color": {"Critical": Color.NEGATIVE, "High": Color.WARNING}},
                {"name": "Fixable", "type": EntityAttributeType.INTEGER},
                {"name": "Total", "type": EntityAttributeType.INTEGER},
            ],
        },
    },
)
