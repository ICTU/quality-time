"""Jacoco Jenkins plugin coverage report time passed collector."""

from base_collectors import JenkinsPluginTimePassedCollector

from .base import JacocoJenkinsPluginBaseClass


class JacocoJenkinsPluginTimePassed(JacocoJenkinsPluginBaseClass, JenkinsPluginTimePassedCollector):
    """Collector for the time passed since the lastest Jacoco Jenkins plugin coverage report."""
