"""Time metric, for testing purposes."""

from collector.metric import MoreIsBetterMetric


class Time(MoreIsBetterMetric):
    """Metric for the number of seconds since epoch."""
    name = "Number of seconds since epoch"
    unit = "seconds"
