"""Metric data needed for notifications."""

from typing import Final

from shared_data_model import DATA_MODEL
from shared.model.metric import Metric
from shared.model.measurement import Measurement
from shared.model.subject import Subject


NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS: Final = 1
NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS_CHANGE: Final = 2


class MetricNotificationData:
    """Handle metric data needed for notifications."""

    def __init__(self, metric: Metric, measurements: list[Measurement], subject: Subject) -> None:
        """Initialise the Notification with metric data."""
        self.metric_name = metric["name"] or DATA_MODEL.metrics[metric["type"]].name
        self.metric_unit = metric["unit"] or DATA_MODEL.metrics[metric["type"]].unit.value
        self.subject_name = subject.get("name") or DATA_MODEL.subjects[subject["type"]].name
        scale = metric["scale"]

        self.new_metric_value = None
        self.old_metric_value = None
        self.new_metric_status = self.__user_friendly_status(None)
        self.old_metric_status = self.__user_friendly_status(None)

        if len(measurements) >= NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS:
            self.new_metric_value = measurements[-1][scale]["value"]
            self.new_metric_status = self.__user_friendly_status(measurements[-1][scale]["status"])

        if len(measurements) >= NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS_CHANGE:
            self.old_metric_value = measurements[-2][scale]["value"]
            self.old_metric_status = self.__user_friendly_status(measurements[-2][scale]["status"])

    @staticmethod
    def __user_friendly_status(metric_status: str | None) -> str:
        """Get the user friendly status name from the data model."""
        statuses = DATA_MODEL.sources["quality_time"].parameters["status"].api_values or {}
        inverted_statuses = {statuses[key]: key for key in statuses}
        human_readable_status, color = (
            str(inverted_statuses.get(metric_status or "unknown", "unknown (white)")).strip(")").split(" (")
        )
        return f"{color} ({human_readable_status})"
