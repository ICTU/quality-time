"""GitHub source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    Branch,
    Branches,
    BranchesToIgnore,
    Days,
    FailureType,
    MergeRequestState,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    PrivateToken,
    StringParameter,
    TargetBranchesToInclude,
    Upvotes,
)

ALL_GITHUB_METRICS = [
     "merge_requests",
]

GITHUB = Source(
    name="GitHub",
    description="GitHub provides a cloud-based hosting service for Git repositories, offering tools for version control, source code management, pull requests, issue tracking, and continuous integration/continuous deployment (CI/CD).",
    url=HttpUrl("https://github.com/about"),
    documentation={
        "generic": """```{note}
documentation about GitHub
```""",
    },
     parameters={
        "url": URL(
            name="GitHub instance URL",
            help="URL of the GitHub instance, with port if necessary, but without path. For example, "
            "'https://github.com'.",
            validate_on=["private_token"],
            metrics=ALL_GITHUB_METRICS,
        ),
        "owner": StringParameter(
            name="Owner (https://github.com/<username>)",
            short_name="owner",
            mandatory=True,
            help_url=HttpUrl("https://docs.github.com/en/account-and-profile"),
            metrics=ALL_GITHUB_METRICS
        ),
        "repository": StringParameter(
            name="Repository (https://github.com/<username>/<repository>)",
            short_name="repository",
            mandatory=True,
            metrics=ALL_GITHUB_METRICS
        ),
        "private_token": PrivateToken(
            name="Personal Access Tokens (with read_api scope)",
            help_url=HttpUrl("https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"),
            metrics=ALL_GITHUB_METRICS,
        ),
        "merge_request_state": MergeRequestState(values=["OPEN", "MERGED", "CLOSED"]),
     },
      entities={
        "merge_requests": Entity(
            name="merge request",
            attributes=[
                EntityAttribute(name="Merge request", key="title", url="url"),
                EntityAttribute(name="Target branch"),
                EntityAttribute(name="State"),
                EntityAttribute(name="Approved"),
                EntityAttribute(name="Upvotes", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Downvotes", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Created", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Updated", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Merged", type=EntityAttributeType.DATETIME),
            ],
        ),
    },
)