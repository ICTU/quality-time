"""Base class for Cobertura Jenkins plugin unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class CoberturaJenkinsPluginCoverageTestCase(SourceCollectorTestCase):
    """Cobertura Jenkins Plugin test case base class."""

    def setUp(self):
        """Extend to set up Cobertura Jenkins plugin test data."""
        super().setUp()
        self.cobertura_jenkins_plugin_json = dict(
            results=dict(
                elements=[
                    dict(denominator=15, numerator=15, name="Conditionals"),
                    dict(denominator=15, numerator=13, name="Lines"),
                ]
            )
        )
