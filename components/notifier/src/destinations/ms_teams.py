"""Microsoft Teams destination.

See https://learn.microsoft.com/en-us/connectors/teams/#microsoft-teams-webhook for the message format.
"""

from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict

import aiohttp

from notifier_utilities.log import get_logger

if TYPE_CHECKING:
    from models.notification import MetricNotificationData, Notification

ICONS_URL = "https://raw.githubusercontent.com/ICTU/quality-time/master/resources/icons"
TIMEOUT = aiohttp.ClientTimeout(total=60)


class Image(TypedDict):
    """Adaptive Card image element."""

    type: Literal["Image"]
    url: str
    size: str


class TextBlock(TypedDict):
    """Adaptive Card text block element."""

    type: Literal["TextBlock"]
    text: str
    wrap: bool
    size: NotRequired[str]
    weight: NotRequired[str]
    isSubtle: NotRequired[bool]
    spacing: NotRequired[str]


class Column(TypedDict):
    """Adaptive Card column."""

    type: Literal["Column"]
    width: str
    items: list[Image | TextBlock]


class ColumnSet(TypedDict):
    """Adaptive Card column set container."""

    type: Literal["ColumnSet"]
    columns: list[Column]


class Fact(TypedDict):
    """Adaptive Card fact."""

    title: str
    value: str


class FactSet(TypedDict):
    """Adaptive Card fact set element."""

    type: Literal["FactSet"]
    facts: list[Fact]


class OpenUrlAction(TypedDict):
    """Adaptive Card action to open a URL."""

    type: Literal["Action.OpenUrl"]
    title: str
    url: str


class ActionSet(TypedDict):
    """Adaptive Card action set element."""

    type: Literal["ActionSet"]
    actions: list[OpenUrlAction]


class Container(TypedDict):
    """Adaptive Card container."""

    type: Literal["Container"]
    separator: bool
    items: list[ColumnSet | FactSet | ActionSet]


class MsTeamsProperties(TypedDict):
    """Microsoft Teams specific Adaptive Card properties."""

    width: str


# Use the functional syntax because "$schema" is not a valid Python identifier:
AdaptiveCard = TypedDict(
    "AdaptiveCard",
    {
        "$schema": str,
        "type": Literal["AdaptiveCard"],
        "version": str,
        "msteams": MsTeamsProperties,
        "summary": str,
        "body": list[TextBlock | Container],
    },
)


class Attachment(TypedDict):
    """Message attachment with an Adaptive Card."""

    contentType: Literal["application/vnd.microsoft.card.adaptive"]
    contentUrl: None
    content: AdaptiveCard


class Message(TypedDict):
    """Message with attachments."""

    type: Literal["message"]
    attachments: list[Attachment]


def metric_container(metric: MetricNotificationData, report_url: str) -> Container:
    """Create an Adaptive Card container for a metric status change."""
    if metric.new_metric_value is None:
        new_value = "unknown"
    else:
        new_value = f"{metric.new_metric_value}{unit_text(metric, metric.new_metric_value)}"
    if metric.old_metric_value is None:
        old_value = "unknown"
    else:
        old_value = f"{metric.old_metric_value}{unit_text(metric, metric.old_metric_value)}"
    old_value_text = " (unchanged)" if metric.new_metric_value == metric.old_metric_value else f", was {old_value}"
    return {
        "type": "Container",
        "separator": True,
        "items": [
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "width": "auto",
                        "items": [{"type": "Image", "url": f"{ICONS_URL}/{metric.status}.png", "size": "Small"}],
                    },
                    {
                        "type": "Column",
                        "width": "stretch",
                        "items": [
                            {"type": "TextBlock", "text": metric.metric_name, "weight": "Bolder", "wrap": True},
                            {
                                "type": "TextBlock",
                                "text": metric.subject_name,
                                "isSubtle": True,
                                "spacing": "None",
                                "wrap": True,
                            },
                        ],
                    },
                ],
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Status:", "value": f"{metric.new_metric_status}, was {metric.old_metric_status}"},
                    {"title": "Value:", "value": f"{new_value}{old_value_text}"},
                ],
            },
            {
                "type": "ActionSet",
                "actions": [
                    {"type": "Action.OpenUrl", "title": "View metric", "url": f"{report_url}#{metric.metric_uuid}"},
                ],
            },
        ],
    }


def unit_text(metric: MetricNotificationData, value: str) -> str:
    """Return the metric unit text, using the correct plural or singular form depending on the value."""
    unit = metric.metric.unit_for_value(value)
    return unit if (not unit or unit.startswith("%")) else f" {unit}"


def create_adaptive_card(notification: Notification) -> AdaptiveCard:
    """Create an Adaptive Card with the notification."""
    title = f"Quality-time notifications for {notification.report_title}"
    metrics = sorted(notification.metrics, key=lambda metric: metric.metric_name)
    return {
        "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "msteams": {"width": "Full"},
        "summary": notification.summary,
        "body": [
            {"type": "TextBlock", "text": title, "size": "Large", "weight": "Bolder", "wrap": True},
            {"type": "TextBlock", "text": notification.summary, "isSubtle": True, "wrap": True},
            *[metric_container(metric, notification.report_url) for metric in metrics],
        ],
    }


def create_message(notification: Notification) -> Message:
    """Create a message with the notification as Adaptive Card attachment.

    Both webhooks created with the Teams Workflows app and legacy Incoming Webhook connectors accept this format.
    """
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": create_adaptive_card(notification),
            },
        ],
    }


async def send_notification(destination: str, notification: Notification) -> None:
    """Send notification to Microsoft Teams using a Webhook."""
    logger = get_logger()
    logger.info("Sending notification to configured teams webhook")
    try:
        async with (
            aiohttp.ClientSession(raise_for_status=True, timeout=TIMEOUT) as session,
            session.post(destination, json=create_message(notification)) as response,
        ):
            logger.debug("Teams webhook responded with status %d", response.status)
    except Exception:
        logger.exception("Could not deliver notification")
