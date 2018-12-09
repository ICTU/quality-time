"""Size metrics."""

from quality_time.metric import Metric


class NCLOC(Metric):
    """Size of source code in Non-Commented Lines of Code."""

    default_target = 50000


class LOC(Metric):
    """Size of source code in Lines of Code."""

    default_target = 75000
