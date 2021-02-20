"""Base classes for Robot Framework collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class RobotFrameworkTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing Robot Framework collectors."""

    SOURCE_TYPE = "robot_framework"
