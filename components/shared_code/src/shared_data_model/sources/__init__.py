"""Data model sources."""

from .anchore import ANCHORE, ANCHORE_JENKINS_PLUGIN
from .axe import AXE_CORE, AXE_CSV, AXE_HTML_REPORTER
from .azure_devops import AZURE_DEVOPS
from .bandit import BANDIT
from .bitbucket import BITBUCKET
from .calendar_date import CALENDAR
from .cargo_audit import CARGO_AUDIT
from .cloc import CLOC
from .cobertura import COBERTURA, COBERTURA_JENKINS_PLUGIN
from .composer import COMPOSER
from .cxsast import CXSAST
from .dependency_track import DEPENDENCY_TRACK
from .gatling import GATLING
from .generic_json import GENERIC_JSON
from .github import GITHUB
from .gitlab import GITLAB
from .grafana_k6 import GRAFANA_K6
from .harbor import HARBOR, HARBOR_JSON
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
from .owasp_dependency_check import OWASP_DEPENDENCY_CHECK_JSON, OWASP_DEPENDENCY_CHECK_XML
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
from .trivy import TRIVY_JSON
from .visual_studio_trx import VISUAL_STUDIO_TRX

SOURCES = {
    "anchore": ANCHORE,
    "anchore_jenkins_plugin": ANCHORE_JENKINS_PLUGIN,
    "axe_core": AXE_CORE,
    "axe_html_reporter": AXE_HTML_REPORTER,
    "axecsv": AXE_CSV,
    "azure_devops": AZURE_DEVOPS,
    "bandit": BANDIT,
    "bitbucket": BITBUCKET,
    "calendar": CALENDAR,
    "cargo_audit": CARGO_AUDIT,
    "cloc": CLOC,
    "cobertura": COBERTURA,
    "cobertura_jenkins_plugin": COBERTURA_JENKINS_PLUGIN,
    "composer": COMPOSER,
    "cxsast": CXSAST,
    "dependency_track": DEPENDENCY_TRACK,
    "gatling": GATLING,
    "generic_json": GENERIC_JSON,
    "github": GITHUB,
    "gitlab": GITLAB,
    "grafana_k6": GRAFANA_K6,
    "harbor": HARBOR,
    "harbor_json": HARBOR_JSON,
    "jacoco": JACOCO,
    "jacoco_jenkins_plugin": JACOCO_JENKINS_PLUGIN,
    "jenkins": JENKINS,
    "jenkins_test_report": JENKINS_TEST_REPORT,
    "jira": JIRA,
    "jmeter_csv": JMETER_CSV,
    "jmeter_json": JMETER_JSON,
    "junit": JUNIT,
    "manual_number": MANUAL_NUMBER,
    "ncover": NCOVER,
    "npm": NPM,
    "ojaudit": OJAUDIT,
    "openvas": OPENVAS,
    "owasp_dependency_check_xml": OWASP_DEPENDENCY_CHECK_XML,
    "owasp_dependency_check_json": OWASP_DEPENDENCY_CHECK_JSON,
    "owasp_zap": OWASP_ZAP,
    "performancetest_runner": PERFORMANCETEST_RUNNER,
    "pip": PIP,
    "pyupio_safety": PYUPIO_SAFETY,
    "quality_time": QUALITY_TIME,
    "robot_framework": ROBOT_FRAMEWORK,
    "robot_framework_jenkins_plugin": ROBOT_FRAMEWORK_JENKINS_PLUGIN,
    "sarif_json": SARIF_JSON,
    "snyk": SNYK,
    "sonarqube": SONARQUBE,
    "testng": TESTNG,
    "trivy_json": TRIVY_JSON,
    "trello": TRELLO,
    "visual_studio_trx": VISUAL_STUDIO_TRX,
}
