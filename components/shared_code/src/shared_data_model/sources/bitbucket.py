"""Bitbucket source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    BranchesToIgnore,
    BranchMergeStatus,
    Days,
    PrivateToken,
    StringParameter,
    MergeRequestState,
    MultipleChoiceParameter,
    TargetBranchesToInclude
)

ALL_GITLAB_METRICS = [
    "inactive_branches",
    "merge_requests",
]

BITBUCKET_BRANCH_HELP_URL = HttpUrl("https://confluence.atlassian.com/bitbucketserver/branches-776639968.html")

BITBUCKET = Source(
    name="Bitbucket",
    description="Bitbucket is a version control platform by Atlassian that supports Git, "
    "enabling developers to collaborate on code with features like pull requests, "
    "CI/CD, and seamless integration with tools like Jira and Trello.",
    url=HttpUrl("https://bitbucket.org/product/guides/getting-started/overview#a-brief-overview-of-bitbucket/"),
    documentation={
        "generic": """```{note}
The pagination for the Bitbucket collector has not yet been implemented,\
and the current limit for retrieving branches for the inactive branches metric using the API is set to 100.\
Pagination will be implemented in a future update.
```""",
    },
    parameters={
        "url": URL(
            name="Bitbucket instance URL",
            help="URL of the Bitbucket instance, with port if necessary, but without path. For example, "
            "'https://bitbucket.org'.",
            validate_on=["private_token"],
            metrics=ALL_GITLAB_METRICS,
        ),
        "owner": StringParameter(
            name="Owner (name of owner of the repository)",
            short_name="owner",
            mandatory=True,
            help_url=HttpUrl("https://support.atlassian.com/bitbucket-cloud/docs/create-a-project/"),
            metrics=ALL_GITLAB_METRICS,
        ),
        "repository": StringParameter(
            name="Repository (name of the repository)",
            short_name="repository",
            help_url=HttpUrl("https://support.atlassian.com/bitbucket-cloud/docs/create-a-git-repository/"),
            mandatory=True,
            metrics=ALL_GITLAB_METRICS,
        ),
        "private_token": PrivateToken(
            name="Private token (with read_api scope)",
            help_url=HttpUrl("https://support.atlassian.com/bitbucket-cloud/docs/create-a-repository-access-token/"),
            metrics=ALL_GITLAB_METRICS,
        ),
        "branches_to_ignore": BranchesToIgnore(help_url=BITBUCKET_BRANCH_HELP_URL),
        "branch_merge_status": BranchMergeStatus(),
        "inactive_days": Days(
            name="Number of days since last commit after which to consider branches inactive",
            short_name="number of days since last commit",
            default_value="7",
            metrics=["inactive_branches"],
        ),
        "merge_request_state": MergeRequestState(
            name="Pull request state",
            values=["Open", "Merged", "Closed"],
            api_values={"Open": "OPEN", "Merged": "MERGED", "Closed": "CLOSED"},
        ),
        "review_decision": MultipleChoiceParameter(
            name="Review decision",
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
        "target_branches_to_include": TargetBranchesToInclude(help_url=BITBUCKET_BRANCH_HELP_URL),
    },
    entities={
        "inactive_branches": Entity(
            name="branch",
            name_plural="branches",
            attributes=[
                EntityAttribute(name="Branch name", key="name", url="url"),
                EntityAttribute(
                    name="Date of most recent commit",
                    key="commit_date",
                    type=EntityAttributeType.DATE,
                ),
                EntityAttribute(name="Merge status"),
            ],
        ),
        "merge_requests": Entity(
            name="merge request",
            attributes=[
                EntityAttribute(name="Merge request", key="title", url="url"),
                EntityAttribute(name="Target branch"),
                EntityAttribute(name="State"),
                EntityAttribute(name="ReviewDecision"),
                EntityAttribute(name="Created", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Updated", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Merged", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Comments", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Thumbs up", type=EntityAttributeType.INTEGER),
            ],
        ),
    },
)
