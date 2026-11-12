"""Report model class."""

from shared.model.report import Report as SharedReport

from .destination import Destination


class Report(SharedReport):
    """Subclass the shared report class to add methods specific for the notifier."""

    def destinations(self) -> list[Destination]:
        """Return the notification destinations of the report that have a webhook."""
        destinations = self.get("notification_destinations", {}).values()
        return [Destination.from_dict(destination) for destination in destinations if destination.get("webhook")]
