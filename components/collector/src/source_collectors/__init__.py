"""Metric collectors per source."""

from .api_source_collectors.azure_devops.issues import AzureDevopsIssues
from .api_source_collectors.azure_devops.jobs import AzureDevopsFailedJobs, AzureDevopsUnusedJobs
from .api_source_collectors.azure_devops.tests import AzureDevopsTests
from .api_source_collectors.azure_devops.unmerged_branches import AzureDevopsUnmergedBranches
from .api_source_collectors.azure_devops.source_up_to_dateness import AzureDevopsSourceUpToDateness
from .api_source_collectors.azure_devops.user_story_points import AzureDevopsUserStoryPoints
from .api_source_collectors.cobertura_jenkins_plugin import (
    CoberturaJenkinsPluginSourceUpToDateness,
    CoberturaJenkinsPluginUncoveredBranches,
    CoberturaJenkinsPluginUncoveredLines,
)
from .api_source_collectors.cxsast import CxSASTSecurityWarnings, CxSASTSourceUpToDateness
from .api_source_collectors.gitlab import (
    GitLabFailedJobs,
    GitLabSourceUpToDateness,
    GitLabUnmergedBranches,
    GitLabUnusedJobs,
)
from .api_source_collectors.jacoco_jenkins_plugin import (
    JacocoJenkinsPluginSourceUpToDateness,
    JacocoJenkinsPluginUncoveredBranches,
    JacocoJenkinsPluginUncoveredLines,
)
from .api_source_collectors.jenkins import JenkinsFailedJobs, JenkinsJobs
from .api_source_collectors.jenkins_test_report import JenkinsTestReportSourceUpToDateness, JenkinsTestReportTests
from .api_source_collectors.jira import (
    JiraIssues,
    JiraManualTestDuration,
    JiraManualTestExecution,
    JiraUserStoryPoints,
    JiraVelocity,
)
from .api_source_collectors.quality_time import QualityTimeMetrics, QualityTimeSourceUpToDateness
from .api_source_collectors.robot_framework_jenkins_plugin import (
    RobotFrameworkJenkinsPluginSourceUpToDateness,
    RobotFrameworkJenkinsPluginTests,
)
from .api_source_collectors.sonarqube import (
    SonarQubeCommentedOutCode,
    SonarQubeComplexUnits,
    SonarQubeDuplicatedLines,
    SonarQubeLOC,
    SonarQubeLongUnits,
    SonarQubeManyParameters,
    SonarQubeSourceUpToDateness,
    SonarQubeSuppressedViolations,
    SonarQubeTests,
    SonarQubeUncoveredBranches,
    SonarQubeUncoveredLines,
    SonarQubeViolations,
)
from .api_source_collectors.trello import TrelloIssues, TrelloSourceUpToDateness
from .api_source_collectors.wekan import WekanIssues, WekanSourceUpToDateness
from .file_source_collectors.anchore import AnchoreSecurityWarnings, AnchoreSourceUpToDateness
from .file_source_collectors.axe_csv import AxeCSVAccessibility
from .file_source_collectors.axe_selenium_python import (
    AxeSeleniumPythonAccessibility,
    AxeSeleniumPythonSourceUpToDateness,
)
from .file_source_collectors.bandit import BanditSecurityWarnings, BanditSourceUpToDateness
from .file_source_collectors.cloc import ClocLOC
from .file_source_collectors.cobertura import (
    CoberturaSourceUpToDateness,
    CoberturaUncoveredBranches,
    CoberturaUncoveredLines,
)
from .file_source_collectors.composer import ComposerDependencies
from .file_source_collectors.generic_json import GenericJSONSecurityWarnings
from .file_source_collectors.jacoco import JacocoSourceUpToDateness, JacocoUncoveredBranches, JacocoUncoveredLines
from .file_source_collectors.junit import JUnitSourceUpToDateness, JUnitTests
from .file_source_collectors.ncover import NCoverSourceUpToDateness
from .file_source_collectors.npm import NpmDependencies
from .file_source_collectors.ojaudit import OJAuditViolations
from .file_source_collectors.openvas import OpenVASSecurityWarnings, OpenVASSourceUpToDateness
from .file_source_collectors.owasp_dependency_check import (
    OWASPDependencyCheckDependencies,
    OWASPDependencyCheckSecurityWarnings,
    OWASPDependencyCheckSourceUpToDateness,
)
from .file_source_collectors.owasp_zap import OWASPZAPSecurityWarnings, OWASPZAPSourceUpToDateness
from .file_source_collectors.performancetest_runner import (
    PerformanceTestRunnerPerformanceTestDuration,
    PerformanceTestRunnerPerformanceTestStability,
    PerformanceTestRunnerScalability,
    PerformanceTestRunnerSlowTransactions,
    PerformanceTestRunnerSourceUpToDateness,
    PerformanceTestRunnerTests,
)
from .file_source_collectors.pip import PipDependencies
from .file_source_collectors.pyupio_safety import PyupioSafetySecurityWarnings
from .file_source_collectors.robot_framework import RobotFrameworkSourceUpToDateness, RobotFrameworkTests
from .file_source_collectors.snyk import SnykSecurityWarnings
from .file_source_collectors.testng import TestNGSourceUpToDateness, TestNGTests
from .local_source_collectors.calendar import CalendarSourceUpToDateness
from .local_source_collectors.manual_number import ManualNumber
from .local_source_collectors.random_number import Random
