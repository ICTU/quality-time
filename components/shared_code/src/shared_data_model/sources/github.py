"""GitHub source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import (
    Entity,
    EntityAttribute,
    EntityAttributeType,
)
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    MergeRequestState,
    MultipleChoiceParameter,
    PrivateToken,
    StringParameter,
    TargetBranchesToInclude,
)

ALL_GITHUB_METRICS = [
    "merge_requests",
]

GITHUB_BRANCH_HELP_URL = HttpUrl(
    "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository"
)

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
            metrics=ALL_GITHUB_METRICS,
        ),
        "repository": StringParameter(
            name="Repository (https://github.com/<username>/<repository>)",
            short_name="repository",
            mandatory=True,
            metrics=ALL_GITHUB_METRICS,
        ),
        "private_token": PrivateToken(
            name="Fine-Grained Personal Access Tokens (with Read scope of the repository)",
            short_name="Fine-Grained Personal Access Tokens",
            help_url=HttpUrl(
                "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
            ),
            metrics=ALL_GITHUB_METRICS,
        ),
        "merge_request_state": MergeRequestState(
            name="Pull request state",
            short_name="PR State",
            values=["Open", "Merged", "Closed"],
            api_values={"Open": "OPEN", "Merged": "MERGED", "Closed": "CLOSED"},
        ),
        "review_decision": MultipleChoiceParameter(
            name="Review Decision",
            values=["Approved", "Changes requested", "Review required", "Unknown"],
            api_values={
                "Approved": "APPROVED",
                "Changes requested": "CHANGES_REQUESTED",
                "Review required": "REVIEW_REQUIRED",
                "Unknown": "?",
            },
            placeholder="all review decisions",
            metrics=["merge_requests"],
        ),
        "target_branches_to_include": TargetBranchesToInclude(
            help_url=GITHUB_BRANCH_HELP_URL
        ),
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
