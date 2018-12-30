"""Size metrics."""

from collector.metric import FewerIsBetterMetric
from collector.type import Measurement


class NCLOC(FewerIsBetterMetric):
    """Size of source code in Non-Commented Lines of Code."""

    name = "Size"
    unit = "non-commented lines of code"
    default_target = Measurement(50000)


class LOC(FewerIsBetterMetric):
    """Size of source code in Lines of Code."""

    name = "Size"
    default_target = Measurement(75000)
    unit = "lines of code"
