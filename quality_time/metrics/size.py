"""Size metrics."""

from quality_time.metric import FewerIsBetterMetric
from quality_time.type import Measurement


class NCLOC(FewerIsBetterMetric):
    """Size of source code in Non-Commented Lines of Code."""

    default_target = Measurement(50000)
    unit = "non-commented lines of code"


class LOC(FewerIsBetterMetric):
    """Size of source code in Lines of Code."""

    default_target = Measurement(75000)
    unit = "lines of code"
