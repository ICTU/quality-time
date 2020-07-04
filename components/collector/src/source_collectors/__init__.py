"""Metric collectors per source."""

from .api_source_collectors.azure_devops import AzureDevopsIssues, AzureDevopsReadyUserStoryPoints
from .api_source_collectors.cxsast import CxSASTSecurityWarnings, CxSASTSourceUpToDateness
from .api_source_collectors.gitlab import (
    GitLabFailedJobs, GitLabUnusedJobs, GitLabSourceUpToDateness, GitLabUnmergedBranches)
from .api_source_collectors.jacoco_jenkins_plugin import (
    JacocoJenkinsPluginUncoveredBranches, JacocoJenkinsPluginUncoveredLines, JacocoJenkinsPluginSourceUpToDateness)
from .api_source_collectors.jenkins import JenkinsFailedJobs, JenkinsJobs
from .api_source_collectors.jenkins_test_report import JenkinsTestReportSourceUpToDateness, JenkinsTestReportTests
from .api_source_collectors.jira import (
    JiraIssues, JiraManualTestDuration, JiraManualTestExecution, JiraReadyUserStoryPoints)
from .api_source_collectors.owasp_dependency_check_jenkins_plugin import (
    OWASPDependencyCheckJenkinsPluginSecurityWarnings, OWASPDependencyCheckJenkinsPluginSourceUpToDateness)
from .api_source_collectors.quality_time import QualityTimeMetrics, QualityTimeSourceUpToDateness
from .api_source_collectors.sonarqube import (
    SonarQubeDuplicatedLines, SonarQubeComplexUnits, SonarQubeCommentedOutCode, SonarQubeLOC, SonarQubeLongUnits,
    SonarQubeManyParameters, SonarQubeSourceUpToDateness, SonarQubeSuppressedViolations, SonarQubeTests,
    SonarQubeUncoveredBranches, SonarQubeUncoveredLines, SonarQubeViolations)
from .api_source_collectors.trello import TrelloIssues, TrelloSourceUpToDateness
from .api_source_collectors.wekan import WekanIssues, WekanSourceUpToDateness

from .file_source_collectors.anchore import AnchoreSecurityWarnings, AnchoreSourceUpToDateness
from .file_source_collectors.axe_csv import AxeCSVAccessibility
from .file_source_collectors.bandit import BanditSecurityWarnings, BanditSourceUpToDateness
from .file_source_collectors.cloc import ClocLOC
from .file_source_collectors.cobertura import (
    CoberturaUncoveredBranches, CoberturaUncoveredLines, CoberturaSourceUpToDateness)
from .file_source_collectors.composer import ComposerDependencies
from .file_source_collectors.jacoco import JacocoSourceUpToDateness, JacocoUncoveredBranches, JacocoUncoveredLines
from .file_source_collectors.junit import JUnitSourceUpToDateness, JUnitTests
from .file_source_collectors.ncover import NCoverSourceUpToDateness
from .file_source_collectors.npm import NpmDependencies
from .file_source_collectors.ojaudit import OJAuditViolations
from .file_source_collectors.openvas import OpenVASSecurityWarnings, OpenVASSourceUpToDateness
from .file_source_collectors.owasp_dependency_check import (
    OWASPDependencyCheckDependencies, OWASPDependencyCheckSecurityWarnings, OWASPDependencyCheckSourceUpToDateness)
from .file_source_collectors.owasp_zap import OWASPZAPSecurityWarnings, OWASPZAPSourceUpToDateness
from .file_source_collectors.performancetest_runner import (
    PerformanceTestRunnerPerformanceTestDuration, PerformanceTestRunnerPerformanceTestStability,
    PerformanceTestRunnerScalability, PerformanceTestRunnerSlowTransactions, PerformanceTestRunnerSourceUpToDateness,
    PerformanceTestRunnerTests)
from .file_source_collectors.pip import PipDependencies
from .file_source_collectors.pyupio_safety import PyupioSafetySecurityWarnings
from .file_source_collectors.robot_framework import RobotFrameworkTests, RobotFrameworkSourceUpToDateness

from .local_source_collectors.calendar import CalendarSourceUpToDateness
from .local_source_collectors.manual_number import ManualNumber
from .local_source_collectors.random_number import Random
