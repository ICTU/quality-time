"""Notification."""

import os
from datetime import datetime, timedelta
from typing import Dict, List


class Notification:
    """Handle notification contents and status."""

    def __init__(self, report, metrics, destination_uuid, destination):
        """Initialise the Notification with the required info."""
        self.report_title = report["title"]
        self.url = report.get("url")
        self.metrics: List[Dict] = metrics
        self.destination_uuid = destination_uuid
        self.destination = destination
        self.creation_time = datetime.now()

    def ready(self):
        """Return whether this notification can be send out."""
        age = datetime.now() - self.creation_time
        minutes = self.destination.get("frequency", int(os.environ.get("NOTIFIER_SLEEP_DURATION", 60)))
        minimal_age = timedelta(minutes=minutes)
        return age >= minimal_age

    def merge_notification(self, new_metrics):
        """Merge new metrics into this notification."""
        for metric in new_metrics:
            self.metrics.append(metric)
