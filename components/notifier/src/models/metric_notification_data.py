"""Metric data needed for notifications."""

from shared_data_model import DATA_MODEL


class MetricNotificationData:  # pylint: disable=too-few-public-methods
    """Handle metric data needed for notifications."""

    def __init__(self, metric, measurements, subject) -> None:
        """Initialise the Notification with metric data."""
        self.metric_name = metric["name"] or f'{DATA_MODEL.metrics[metric["type"]].name}'
        self.metric_unit = metric["unit"] or f'{DATA_MODEL.metrics[metric["type"]].unit}'
        self.subject_name = subject.get("name") or DATA_MODEL.subjects[subject["type"]].name
        scale = metric["scale"]

        self.new_metric_value = None
        self.old_metric_value = None
        self.new_metric_status = self.__user_friendly_status(None)
        self.old_metric_status = self.__user_friendly_status(None)

        if len(measurements) >= 1:
            self.new_metric_value = measurements[-1][scale]["value"]
            self.new_metric_status = self.__user_friendly_status(measurements[-1][scale]["status"])

        if len(measurements) >= 2:
            self.old_metric_value = measurements[-2][scale]["value"]
            self.old_metric_status = self.__user_friendly_status(measurements[-2][scale]["status"])

    @staticmethod
    def __user_friendly_status(metric_status) -> str:
        """Get the user friendly status name from the data model."""
        statuses = DATA_MODEL.sources["quality_time"].parameters["status"].api_values or {}
        inverted_statuses = {statuses[key]: key for key in statuses}
        human_readable_status, color = (
            str(inverted_statuses.get(metric_status, "unknown (white)")).strip(")").split(" (")
        )
        return f"{color} ({human_readable_status})"
