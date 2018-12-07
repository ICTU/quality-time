"""Size metrics."""

from quality_time.metric import Metric


class NonCommentedLinesOfCode(Metric):
    """Size of source code in Non-Commented Lines of Code."""

    API = "ncloc"


class LinesOfCode(Metric):
    """Size of source code in Non-Commented Lines of Code."""

    API = "loc"
