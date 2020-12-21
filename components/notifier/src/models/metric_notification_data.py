"""Metric data needed for notifications."""


class MetricNotificationData:  # pylint: disable=too-few-public-methods
    """Handle metric data needed for notifications."""

    def __init__(self, metric, data_model, reason: str) -> None:
        """Initialise the Notification with metric data."""
        recent_measurements = metric["recent_measurements"]
        scale = metric["scale"]
        self.metric_name = metric["name"] or f'{data_model["metrics"][metric["type"]]["name"]}'
        self.metric_unit = metric["unit"] or f'{data_model["metrics"][metric["type"]]["unit"]}'
        self.new_metric_value = recent_measurements[-1][scale]["value"]
        self.old_metric_value = recent_measurements[-2][scale]["value"]
        self.new_metric_status = self.__get_correct_userfriendly_status(
            data_model["sources"]["quality_time"]["parameters"]["status"]["api_values"],
            recent_measurements[-1][scale]["status"])
        self.old_metric_status = self.__get_correct_userfriendly_status(
            data_model["sources"]["quality_time"]["parameters"]["status"]["api_values"],
            recent_measurements[-2][scale]["status"])
        self.reason = reason

    @staticmethod
    def __get_correct_userfriendly_status(userfriendly_statuses, metric_status) -> str:
        """Get the user friendly status name."""
        inverted_statuses = {userfriendly_statuses[key]: key for key in userfriendly_statuses}
        human_readable_status, color = str(inverted_statuses[metric_status]).strip(")").split(" (")
        return f"{color} ({human_readable_status})"
