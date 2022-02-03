"""Cobertura Jenkins plugin coverage report time passed collector."""

from base_collectors import JenkinsPluginTimePassedCollector

from .base import CoberturaJenkinsPluginBaseClass


class CoberturaJenkinsPluginTimePassed(CoberturaJenkinsPluginBaseClass, JenkinsPluginTimePassedCollector):
    """Collector for the time passed since the latest Cobertura Jenkins plugin coverage report."""
