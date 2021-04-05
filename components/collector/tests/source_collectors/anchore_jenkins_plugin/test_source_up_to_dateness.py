"""Unit tests for the Anchore Jenkins plugin source up-to-dateness collector."""

from ..jenkins_plugin_test_case import JenkinsPluginSourceUpToDatenessMixin
from ..source_collector_test_case import SourceCollectorTestCase


class AnchoreJenkinsPluginSourceUpToDatenessTest(
    JenkinsPluginSourceUpToDatenessMixin, SourceCollectorTestCase
):  # skipcq: PTC-W0046
    """Unit tests for the Anchore Jenkins plugin source up-to-dateness collector."""

    SOURCE_TYPE = "anchore_jenkins_plugin"
