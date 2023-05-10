"""Base class for unit tests for the Axe-core report."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class AxeCoreTestCase(SourceCollectorTestCase):
    """Base class for testing Axe-core collectors."""

    SOURCE_TYPE = "axe_core"
