"""Trello source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    Days,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    StringParameter,
)

ALL_TRELLO_METRICS = ["issues", "source_up_to_dateness"]

ISSUE_ENTITY = Entity(
    name="issue",
    attributes=[
        EntityAttribute(name="Title", url="url"),
        EntityAttribute(name="List"),
        EntityAttribute(name="Due date", type=EntityAttributeType.DATETIME),
        EntityAttribute(name="Date of last activity", key="date_last_activity", type=EntityAttributeType.DATETIME),
    ],
)

INACTIVE_DAYS_PARAMETER = Days(
    name="Number of days without activity after which to consider cards inactive",
    short_name="number of days without activity",
    default_value="30",
    metrics=["issues"],
)

LISTS_TO_IGNORE_PARAMETER = MultipleChoiceWithAdditionParameter(
    name="Lists to ignore (title or id)",
    short_name="lists to ignore",
    metrics=ALL_TRELLO_METRICS,
)

CARDS_TO_COUNT_PARAMETER = MultipleChoiceParameter(
    name="Cards to count",
    short_name="cards",
    placeholder="all cards",
    values=["inactive", "overdue"],
    metrics=["issues"],
)

TRELLO_URL = "https://trello.com"
TRELLO_APP_KEY_URL = HttpUrl(f"{TRELLO_URL}/app-key")

TRELLO = Source(
    name="Trello",
    description="Trello is a collaboration tool that organizes projects into boards.",
    url=HttpUrl(TRELLO_URL),
    parameters={
        "url": URL(
            name="URL",
            validate_on=["api_key", "token"],
            default_value=TRELLO_URL,
            metrics=ALL_TRELLO_METRICS,
        ),
        "api_key": StringParameter(
            name="API key",
            short_name="API key",
            help_url=TRELLO_APP_KEY_URL,
            metrics=ALL_TRELLO_METRICS,
        ),
        "token": StringParameter(
            name="Token",
            help_url=TRELLO_APP_KEY_URL,
            metrics=ALL_TRELLO_METRICS,
        ),
        "board": StringParameter(
            name="Board (title or id)",
            short_name="board",
            help_url=HttpUrl(f"{TRELLO_URL}/1/members/me/boards?fields=name"),
            mandatory=True,
            metrics=ALL_TRELLO_METRICS,
        ),
        "lists_to_ignore": LISTS_TO_IGNORE_PARAMETER,
        "cards_to_count": CARDS_TO_COUNT_PARAMETER,
        "inactive_days": INACTIVE_DAYS_PARAMETER,
    },
    entities={"issues": ISSUE_ENTITY},
)
