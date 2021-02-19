"""Base classes for JaCoCo Jenkins plugin unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class JaCoCoJenkinsPluginCoverageTestCase(SourceCollectorTestCase):
    """JaCoCo Jenkins plugin coverage base class."""

    def setUp(self):
        """Extend to set up JaCoCo Jenkins plugin JSON data."""
        super().setUp()
        self.jacoco_jenkins_plugin_json = dict(
            branchCoverage=dict(total=6, missed=2), lineCoverage=dict(total=6, missed=2)
        )
