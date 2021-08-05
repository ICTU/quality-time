"""Metric data needed for notifications."""


class MetricNotificationData:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Handle metric data needed for notifications."""

    def __init__(self, metric, subject, data_model, reason: str) -> None:
        """Initialise the Notification with metric data."""
        self.metric_name = metric["name"] or f'{data_model["metrics"][metric["type"]]["name"]}'
        self.metric_unit = metric["unit"] or f'{data_model["metrics"][metric["type"]]["unit"]}'
        self.subject_name = subject.get("name") or data_model["subjects"][subject["type"]]["name"]
        recent_measurements = metric["recent_measurements"]
        scale = metric["scale"]

        self.new_metric_value = None
        self.old_metric_value = None
        self.new_metric_status = self.__user_friendly_status(data_model, None)
        self.old_metric_status = self.__user_friendly_status(data_model, None)

        if len(recent_measurements) >= 1:
            self.new_metric_value = recent_measurements[-1][scale]["value"]
            self.new_metric_status = self.__user_friendly_status(data_model, recent_measurements[-1][scale]["status"])

        if len(recent_measurements) >= 2:
            self.old_metric_value = recent_measurements[-2][scale]["value"]
            self.old_metric_status = self.__user_friendly_status(data_model, recent_measurements[-2][scale]["status"])

        self.reason = reason

    @staticmethod
    def __user_friendly_status(data_model, metric_status) -> str:
        """Get the user friendly status name from the data model."""
        statuses = data_model["sources"]["quality_time"]["parameters"]["status"]["api_values"]
        inverted_statuses = {statuses[key]: key for key in statuses}
        human_readable_status, color = (
            str(inverted_statuses.get(metric_status, "unknown (white)")).strip(")").split(" (")
        )
        return f"{color} ({human_readable_status})"
