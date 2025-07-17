"""Metric data needed for notifications."""

from typing import TYPE_CHECKING, Final

from shared_data_model import DATA_MODEL

if TYPE_CHECKING:
    from shared.model.measurement import Measurement
    from shared.model.metric import Metric, MetricId
    from shared.model.subject import Subject

NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS: Final = 1
NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS_CHANGE: Final = 2
LAST: Final = -NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS
LAST_BUT_ONE: Final = -NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS_CHANGE


class MetricNotificationData:
    """Handle metric data needed for notifications."""

    def __init__(
        self,
        metric: Metric,
        metric_uuid: MetricId,
        measurements: list[Measurement],
        subject: Subject,
    ) -> None:
        """Initialise the Notification with metric data."""
        self.metric = metric
        self.metric_uuid = metric_uuid
        self.measurements = measurements
        self.metric_name = metric["name"] or DATA_MODEL.metrics[metric["type"]].name
        self.metric_unit = metric["unit"] or DATA_MODEL.metrics[metric["type"]].unit.value
        self.subject_name = subject.get("name") or DATA_MODEL.all_subjects[subject["type"]].name
        self.scale = metric.scale()
        self.status = self.__status(LAST)
        self.new_metric_value = self.__value(LAST)
        self.new_metric_status = self.__user_friendly_status(LAST)
        self.old_metric_value = self.__value(LAST_BUT_ONE)
        self.old_metric_status = self.__user_friendly_status(LAST_BUT_ONE)

    def __user_friendly_status(self, index: int) -> str:
        """Get the user friendly status name from the data model."""
        statuses = DATA_MODEL.sources["quality_time"].parameters["status"].api_values or {}
        inverted_statuses = {statuses[key]: key for key in statuses}
        return inverted_statuses.get(self.__status(index), "unknown (white)")

    def __status(self, index: int) -> str:
        """Return the measurement status."""
        if (measurement := self.__measurement(index)) and (status := measurement[self.scale]["status"]):
            return str(status)
        return "unknown"

    def __value(self, index: int) -> str | None:
        """Return the measurement value."""
        return measurement[self.scale]["value"] if (measurement := self.__measurement(index)) else None

    def __measurement(self, index: int) -> Measurement | None:
        """Return the measurement."""
        try:
            return self.measurements[index]
        except IndexError:
            return None
