"""Jacoco Jenkins plugin coverage report source up-to-dateness collector."""

from base_collectors import JenkinsPluginSourceUpToDatenessCollector

from .base import JacocoJenkinsPluginBaseClass


class JacocoJenkinsPluginSourceUpToDateness(JacocoJenkinsPluginBaseClass, JenkinsPluginSourceUpToDatenessCollector):
    """Collector for the up-to-dateness of the Jacoco Jenkins plugin coverage report."""
