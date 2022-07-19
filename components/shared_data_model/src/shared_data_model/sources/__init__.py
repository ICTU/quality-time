"""Data model sources."""

from ..meta.source import Sources

from .anchore import ANCHORE, ANCHORE_JENKINS_PLUGIN
from .axe import AXE_CORE, AXE_CSV, AXE_HTML_REPORTER
from .azure_devops import AZURE_DEVOPS
from .bandit import BANDIT
from .calendar import CALENDAR
from .cloc import CLOC
from .cobertura import COBERTURA, COBERTURA_JENKINS_PLUGIN
from .composer import COMPOSER
from .cxsast import CXSAST
from .gatling import GATLING
from .generic_json import GENERIC_JSON
from .gitlab import GITLAB
from .jacoco import JACOCO, JACOCO_JENKINS_PLUGIN
from .jenkins import JENKINS, JENKINS_TEST_REPORT
from .jira import JIRA
from .jmeter import JMETER_CSV, JMETER_JSON
from .junit import JUNIT
from .manual_number import MANUAL_NUMBER
from .ncover import NCOVER
from .npm import NPM
from .ojaudit import OJAUDIT
from .openvas import OPENVAS
from .owasp_dependency_check import OWASP_DEPENDENCY_CHECK
from .owasp_zap import OWASP_ZAP
from .performancetest_runner import PERFORMANCETEST_RUNNER
from .pip import PIP
from .pyupio_safety import PYUPIO_SAFETY
from .quality_time import QUALITY_TIME
from .robot_framework import ROBOT_FRAMEWORK, ROBOT_FRAMEWORK_JENKINS_PLUGIN
from .sarif import SARIF_JSON
from .snyk import SNYK
from .sonarqube import SONARQUBE
from .testng import TESTNG
from .trello import TRELLO


SOURCES = Sources.parse_obj(
    dict(
        anchore=ANCHORE,
        anchore_jenkins_plugin=ANCHORE_JENKINS_PLUGIN,
        axe_core=AXE_CORE,
        axe_html_reporter=AXE_HTML_REPORTER,
        axecsv=AXE_CSV,
        azure_devops=AZURE_DEVOPS,
        bandit=BANDIT,
        calendar=CALENDAR,
        cloc=CLOC,
        cobertura=COBERTURA,
        cobertura_jenkins_plugin=COBERTURA_JENKINS_PLUGIN,
        composer=COMPOSER,
        cxsast=CXSAST,
        gatling=GATLING,
        generic_json=GENERIC_JSON,
        gitlab=GITLAB,
        jacoco=JACOCO,
        jacoco_jenkins_plugin=JACOCO_JENKINS_PLUGIN,
        jenkins=JENKINS,
        jenkins_test_report=JENKINS_TEST_REPORT,
        jira=JIRA,
        jmeter_csv=JMETER_CSV,
        jmeter_json=JMETER_JSON,
        junit=JUNIT,
        manual_number=MANUAL_NUMBER,
        ncover=NCOVER,
        npm=NPM,
        ojaudit=OJAUDIT,
        openvas=OPENVAS,
        owasp_dependency_check=OWASP_DEPENDENCY_CHECK,
        owasp_zap=OWASP_ZAP,
        performancetest_runner=PERFORMANCETEST_RUNNER,
        pip=PIP,
        pyupio_safety=PYUPIO_SAFETY,
        quality_time=QUALITY_TIME,
        robot_framework=ROBOT_FRAMEWORK,
        robot_framework_jenkins_plugin=ROBOT_FRAMEWORK_JENKINS_PLUGIN,
        sarif_json=SARIF_JSON,
        snyk=SNYK,
        sonarqube=SONARQUBE,
        testng=TESTNG,
        trello=TRELLO,
    )
)
