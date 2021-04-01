"""Base class for unit tests for the Axe-core report."""

from ..source_collector_test_case import SourceCollectorTestCase


class AxeCoreTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing Axe-core collectors."""

    SOURCE_TYPE = "axe_core"
