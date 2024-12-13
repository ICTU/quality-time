"""Bitbucket source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    Branch,
    Branches,
    BranchesToIgnore,
    BranchMergeStatus,
    Days,
    FailureType,
    MergeRequestState,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    PrivateToken,
    ResultType,
    StringParameter,
    TargetBranchesToInclude,
)

BITBUCKET_BRANCH_HELP_URL = HttpUrl("https://confluence.atlassian.com/bitbucketserver/branches-776639968.html")

BITBUCKET = Source(
    name="Bitbucket",
    description="Bitbucket Cloud is a Git based code hosting and collaboration tool, built for teams."
                "Bitbucket's best-in-class Jira and Trello integrations are designed to bring the entire software team together to execute on a project.",
    url=HttpUrl("https://bitbucket.org/product/guides/getting-started/overview#a-brief-overview-of-bitbucket/"),
    documentation={},
    parameters={
        "url": URL(
            name="Bitbucket instance URL",
            help="URL of the Bitbucket instance, with port if necessary, but without path. For example, "
            "'https://bitbucket.org'.",
            validate_on=["private_token"],
            metrics=["inactive_branches"],
        ),
        "project": StringParameter(
            name="Project (name with namespace or id)",
            short_name="project",
            mandatory=True,
            help_url=HttpUrl("https://support.atlassian.com/bitbucket-cloud/docs/create-a-project/"),
            metrics=[
                "inactive_branches",
            ],
        ),
        "private_token": PrivateToken(
            name="Private token (with read_api scope)",
            help_url=HttpUrl("https://support.atlassian.com/bitbucket-cloud/docs/create-a-repository-access-token/"),
            metrics=["inactive_branches"],
        ),
        "branches_to_ignore": BranchesToIgnore(help_url=BITBUCKET_BRANCH_HELP_URL),
        "branch_merge_status": BranchMergeStatus(),
        "inactive_days": Days(
            name="Number of days since last commit after which to consider branches inactive",
            short_name="number of days since last commit",
            default_value="7",
            metrics=["inactive_branches"],
        ),
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
        )
    },
)
