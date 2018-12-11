"""Size metrics."""

from quality_time.metric import Metric
from quality_time.type import Measurement


class NCLOC(Metric):
    """Size of source code in Non-Commented Lines of Code."""

    default_target = Measurement(50000)


class LOC(Metric):
    """Size of source code in Lines of Code."""

    default_target = Measurement(75000)
