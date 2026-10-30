"""Metric data needed for notifications."""

from datetime import datetime, time, timedelta
from functools import cached_property
from typing import TYPE_CHECKING, Final

from dateutil.tz import tzlocal

from shared.utils.date_time import parse_datetime
from shared_data_model import DATA_MODEL

from notifier_utilities.log import get_logger

if TYPE_CHECKING:
    from shared.model.measurement import Measurement
    from shared.model.metric import Metric
    from shared.model.subject import Subject
    from shared.utils.type import MetricId

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
        self.report = subject.report
        metric_type = DATA_MODEL.metrics[metric["type"]]
        self.metric_name = metric.get("name") or metric_type.name
        self.subject_name = subject.get("name") or DATA_MODEL.all_subjects[subject["type"]].name
        self.scale = metric.scale()
        self.status = self.__status(LAST)
        self.new_metric_value = self.__value(LAST)
        self.new_metric_status = self.__user_friendly_status(LAST)
        self.old_metric_value = self.__value(LAST_BUT_ONE)
        self.old_metric_status = self.__user_friendly_status(LAST_BUT_ONE)

    @cached_property
    def deadline(self) -> datetime | None:
        """Return the deadline for addressing the metric, if any.

        Note that the frontend uses the same logic to determine the time left, in src/utils.jsx.
        """
        if self.status == "debt_target_met":
            if debt_end_date := self.metric.get("debt_end_date"):
                # The debt end date is a date, or a UTC datetime if set via the frontend's date picker:
                try:
                    end_date = parse_datetime(debt_end_date).astimezone(tzlocal()).date()
                except ValueError, OverflowError:
                    logger = get_logger()
                    logger.warning("Ignoring invalid debt end date %s of metric %s", debt_end_date, self.metric_uuid)
                    return None
                return datetime.combine(end_date, time(23, 59, 59), tzinfo=tzlocal())
            return None
        desired_response_time = self.report.desired_response_time(self.status)
        measurement = self.__measurement(LAST)
        status_start = measurement[self.scale].get("status_start") if measurement else None
        if desired_response_time is None or not status_start:
            return None
        return datetime.fromisoformat(status_start) + timedelta(days=desired_response_time)

    def status_changed_after(self, timestamp: datetime) -> bool:
        """Return whether the metric got a new status after the timestamp."""
        if len(self.measurements) < NR_OF_MEASUREMENTS_NEEDED_TO_DETERMINE_STATUS_CHANGE:
            return False
        status_changed = self.__status(LAST_BUT_ONE) != self.status
        change_was_recent = datetime.fromisoformat(self.measurements[LAST]["start"]) > timestamp
        return status_changed and change_was_recent

    def deadline_on_or_before(self, timestamp: datetime) -> bool:
        """Return whether the metric has a deadline on or before the timestamp."""
        return self.deadline is not None and self.deadline <= timestamp

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
