"""NCover uncovered branches collector."""

from .base import NCoverCoverageBase


class NCoverUncoveredBranches(NCoverCoverageBase):
    """Collector to get the uncovered branches."""

    coverage_type = "branch"
