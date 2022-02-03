"""Unit tests for the Cobertura Jenkins plugin time passed collector."""

from ..jenkins_plugin_test_case import JenkinsPluginTimePassedMixin

from .base import CoberturaJenkinsPluginTestCase


class CoberturaJenkinsPluginTimePassedTest(  # skipcq: PTC-W0046
    JenkinsPluginTimePassedMixin, CoberturaJenkinsPluginTestCase
):
    """Unit tests for the Cobertura Jenkins plugin time passed collector."""
