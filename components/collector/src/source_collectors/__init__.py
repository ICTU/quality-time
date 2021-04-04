"""Metric collectors per source."""

from .anchore.security_warnings import AnchoreSecurityWarnings
from .anchore.source_up_to_dateness import AnchoreSourceUpToDateness

from .anchore_jenkins_plugin.security_warnings import AnchoreJenkinsPluginSecurityWarnings
from .anchore_jenkins_plugin.source_up_to_dateness import AnchoreJenkinsPluginSourceUpToDateness

from .axe_core.accessibility import AxeCoreAccessibility
from .axe_core.source_up_to_dateness import AxeCoreSourceUpToDateness
from .axe_core.source_version import AxeCoreSourceVersion

from .axe_csv.accessibility import AxeCSVAccessibility

from .azure_devops.failed_jobs import AzureDevopsFailedJobs
from .azure_devops.issues import AzureDevopsIssues
from .azure_devops.merge_requests import AzureDevopsMergeRequests
from .azure_devops.source_up_to_dateness import AzureDevopsSourceUpToDateness
from .azure_devops.tests import AzureDevopsTests
from .azure_devops.unmerged_branches import AzureDevopsUnmergedBranches
from .azure_devops.unused_jobs import AzureDevopsUnusedJobs
from .azure_devops.user_story_points import AzureDevopsUserStoryPoints

from .bandit.security_warnings import BanditSecurityWarnings
from .bandit.source_up_to_dateness import BanditSourceUpToDateness

from .calendar.source_up_to_dateness import CalendarSourceUpToDateness

from .cloc.loc import ClocLOC
from .cloc.source_version import ClocSourceVersion

from .cobertura.source_up_to_dateness import CoberturaSourceUpToDateness
from .cobertura.source_version import CoberturaSourceVersion
from .cobertura.uncovered_branches import CoberturaUncoveredBranches
from .cobertura.uncovered_lines import CoberturaUncoveredLines

from .cobertura_jenkins_plugin.source_up_to_dateness import CoberturaJenkinsPluginSourceUpToDateness
from .cobertura_jenkins_plugin.uncovered_branches import CoberturaJenkinsPluginUncoveredBranches
from .cobertura_jenkins_plugin.uncovered_lines import CoberturaJenkinsPluginUncoveredLines

from .composer.dependencies import ComposerDependencies

from .cxsast.security_warnings import CxSASTSecurityWarnings
from .cxsast.source_up_to_dateness import CxSASTSourceUpToDateness
from .cxsast.source_version import CxSASTSourceVersion

from .generic_json.security_warnings import GenericJSONSecurityWarnings

from .gitlab.failed_jobs import GitLabFailedJobs
from .gitlab.merge_requests import GitLabMergeRequests
from .gitlab.source_up_to_dateness import GitLabSourceUpToDateness
from .gitlab.source_version import GitLabSourceVersion
from .gitlab.unmerged_branches import GitLabUnmergedBranches
from .gitlab.unused_jobs import GitLabUnusedJobs

from .jacoco.source_up_to_dateness import JacocoSourceUpToDateness
from .jacoco.uncovered_branches import JacocoUncoveredBranches
from .jacoco.uncovered_lines import JacocoUncoveredLines

from .jacoco_jenkins_plugin.source_up_to_dateness import JacocoJenkinsPluginSourceUpToDateness
from .jacoco_jenkins_plugin.uncovered_branches import JacocoJenkinsPluginUncoveredBranches
from .jacoco_jenkins_plugin.uncovered_lines import JacocoJenkinsPluginUncoveredLines

from .jenkins.failed_jobs import JenkinsFailedJobs
from .jenkins.source_up_to_dateness import JenkinsSourceUpToDateness
from .jenkins.source_version import JenkinsSourceVersion
from .jenkins.unused_jobs import JenkinsUnusedJobs

from .jenkins_test_report.source_up_to_dateness import JenkinsTestReportSourceUpToDateness
from .jenkins_test_report.tests import JenkinsTestReportTests

from .jira.issues import JiraIssues
from .jira.manual_test_duration import JiraManualTestDuration
from .jira.manual_test_execution import JiraManualTestExecution
from .jira.source_version import JiraSourceVersion
from .jira.user_story_points import JiraUserStoryPoints
from .jira.velocity import JiraVelocity

from .junit.source_up_to_dateness import JUnitSourceUpToDateness
from .junit.tests import JUnitTests

from .manual_number.all_metrics import ManualNumber

from .ncover.uncovered_branches import NCoverUncoveredBranches
from .ncover.uncovered_lines import NCoverUncoveredLines
from .ncover.source_up_to_dateness import NCoverSourceUpToDateness

from .npm.dependencies import NpmDependencies

from .ojaudit.violations import OJAuditViolations

from .openvas.security_warnings import OpenVASSecurityWarnings
from .openvas.source_up_to_dateness import OpenVASSourceUpToDateness
from .openvas.source_version import OpenVASSourceVersion

from .owasp_dependency_check.dependencies import OWASPDependencyCheckDependencies
from .owasp_dependency_check.security_warnings import OWASPDependencyCheckSecurityWarnings
from .owasp_dependency_check.source_up_to_dateness import OWASPDependencyCheckSourceUpToDateness
from .owasp_dependency_check.source_version import OWASPDependencyCheckSourceVersion

from .owasp_zap.security_warnings import OWASPZAPSecurityWarnings
from .owasp_zap.source_up_to_dateness import OWASPZAPSourceUpToDateness
from .owasp_zap.source_version import OWASPZAPSourceVersion

from .performancetest_runner.performancetest_duration import PerformanceTestRunnerPerformanceTestDuration
from .performancetest_runner.performancetest_scalability import PerformanceTestRunnerScalability
from .performancetest_runner.performancetest_stability import PerformanceTestRunnerPerformanceTestStability
from .performancetest_runner.slow_transactions import PerformanceTestRunnerSlowTransactions
from .performancetest_runner.source_up_to_dateness import PerformanceTestRunnerSourceUpToDateness
from .performancetest_runner.tests import PerformanceTestRunnerTests

from .pip.dependencies import PipDependencies

from .pyupio_safety.security_warnings import PyupioSafetySecurityWarnings

from .quality_time.metrics import QualityTimeMetrics
from .quality_time.source_up_to_dateness import QualityTimeSourceUpToDateness
from .quality_time.source_version import QualityTimeSourceVersion

from .random_number.all_metrics import Random

from .robot_framework.source_up_to_dateness import RobotFrameworkSourceUpToDateness
from .robot_framework.source_version import RobotFrameworkSourceVersion
from .robot_framework.tests import RobotFrameworkTests

from .robot_framework_jenkins_plugin.source_up_to_dateness import RobotFrameworkJenkinsPluginSourceUpToDateness
from .robot_framework_jenkins_plugin.tests import RobotFrameworkJenkinsPluginTests

from .snyk.security_warnings import SnykSecurityWarnings

from .sonarqube.commented_out_code import SonarQubeCommentedOutCode
from .sonarqube.complex_units import SonarQubeComplexUnits
from .sonarqube.duplicated_lines import SonarQubeDuplicatedLines
from .sonarqube.loc import SonarQubeLOC
from .sonarqube.long_units import SonarQubeLongUnits
from .sonarqube.many_parameters import SonarQubeManyParameters
from .sonarqube.remediation_effort import SonarQubeRemediationEffort
from .sonarqube.security_warnings import SonarQubeSecurityWarnings
from .sonarqube.source_up_to_dateness import SonarQubeSourceUpToDateness
from .sonarqube.source_version import SonarQubeSourceVersion
from .sonarqube.suppressed_violations import SonarQubeSuppressedViolations
from .sonarqube.tests import SonarQubeTests
from .sonarqube.uncovered_branches import SonarQubeUncoveredBranches
from .sonarqube.uncovered_lines import SonarQubeUncoveredLines
from .sonarqube.violations import SonarQubeViolations

from .testng.source_up_to_dateness import TestNGSourceUpToDateness
from .testng.tests import TestNGTests

from .trello.issues import TrelloIssues
from .trello.source_up_to_dateness import TrelloSourceUpToDateness

from .wekan.issues import WekanIssues
from .wekan.source_up_to_dateness import WekanSourceUpToDateness
