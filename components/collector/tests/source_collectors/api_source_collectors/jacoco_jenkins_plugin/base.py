"""Base classes for JaCoCo Jenkins plugin unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class JaCoCoJenkinsPluginTestCase(SourceCollectorTestCase):
    """JaCoCo Jenkins plugin coverage base class."""

    SOURCE_TYPE = "jacoco_jenkins_plugin"
