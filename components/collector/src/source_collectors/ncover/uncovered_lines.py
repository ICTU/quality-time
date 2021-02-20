"""NCover uncovered lines collector."""

from .base import NCoverCoverageBase


class NCoverUncoveredLines(NCoverCoverageBase):
    """Collector to get the uncovered lines.

    Since NCover doesn't report lines, but sequence points, we use those.
    See http://www.ncover.com/blog/code-coverage-metrics-sequence-point-coverage/.
    """

    coverage_type = "sequencePoint"
