"""Metric collectors per source."""

from .api_source_collectors.azure_devops.issues import AzureDevopsIssues
from .api_source_collectors.azure_devops.jobs import AzureDevopsFailedJobs, AzureDevopsUnusedJobs
from .api_source_collectors.azure_devops.merge_requests import AzureDevopsMergeRequests
from .api_source_collectors.azure_devops.tests import AzureDevopsTests
from .api_source_collectors.azure_devops.unmerged_branches import AzureDevopsUnmergedBranches
from .api_source_collectors.azure_devops.source_up_to_dateness import AzureDevopsSourceUpToDateness
from .api_source_collectors.azure_devops.user_story_points import AzureDevopsUserStoryPoints
from .api_source_collectors.cobertura_jenkins_plugin.source_up_to_dateness import (
    CoberturaJenkinsPluginSourceUpToDateness,
)
from .api_source_collectors.cobertura_jenkins_plugin.uncovered_branches import CoberturaJenkinsPluginUncoveredBranches
from .api_source_collectors.cobertura_jenkins_plugin.uncovered_lines import CoberturaJenkinsPluginUncoveredLines
from .api_source_collectors.cxsast import CxSASTSecurityWarnings, CxSASTSourceUpToDateness
from .api_source_collectors.gitlab.jobs import GitLabFailedJobs, GitLabUnusedJobs
from .api_source_collectors.gitlab.merge_requests import GitLabMergeRequests
from .api_source_collectors.gitlab.source_up_to_dateness import GitLabSourceUpToDateness
from .api_source_collectors.gitlab.unmerged_branches import GitLabUnmergedBranches
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
from .api_source_collectors.sonarqube.commented_out_code import SonarQubeCommentedOutCode
from .api_source_collectors.sonarqube.complex_units import SonarQubeComplexUnits
from .api_source_collectors.sonarqube.duplicated_lines import SonarQubeDuplicatedLines
from .api_source_collectors.sonarqube.loc import SonarQubeLOC
from .api_source_collectors.sonarqube.long_units import SonarQubeLongUnits
from .api_source_collectors.sonarqube.many_parameters import SonarQubeManyParameters
from .api_source_collectors.sonarqube.remediation_effort import SonarQubeRemediationEffort
from .api_source_collectors.sonarqube.security_warnings import SonarQubeSecurityWarnings
from .api_source_collectors.sonarqube.source_up_to_dateness import SonarQubeSourceUpToDateness
from .api_source_collectors.sonarqube.suppressed_violations import SonarQubeSuppressedViolations
from .api_source_collectors.sonarqube.tests import SonarQubeTests
from .api_source_collectors.sonarqube.uncovered_branches import SonarQubeUncoveredBranches
from .api_source_collectors.sonarqube.uncovered_lines import SonarQubeUncoveredLines
from .api_source_collectors.sonarqube.violations import SonarQubeViolations
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
