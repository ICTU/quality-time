# Quality-time metrics and sources

This document lists all [metrics](#metrics) that *Quality-time* can measure and all [sources](#sources) that *Quality-time* can use to measure the metrics. For each [supported combination of metric and source](#supported-metric-source-combinations), it lists the parameters that can be used to configure the source.

## Metrics

| Name | Description | Default target | Scale(s) | Default tags | Sources¹ |
| :--- | :---------- | :------------- | :------- | :----------- | :------- |
| Accessibility violations | The number of accessibility violations in the web user interface of the software. | ≦ 0 violations | count | accessibility | [Axe CSV](#accessibility-violations-from-axe-csv), [Axe-core](#accessibility-violations-from-axe-core) |
| Commented out code | The number of blocks of commented out lines of code. | ≦ 0 blocks | count | maintainability | [SonarQube](#commented-out-code-from-sonarqube) |
| Complex units | The amount of units (classes, functions, methods, files) that are too complex. | ≦ 0 complex units | count (default), percentage | maintainability, testability | [SonarQube](#complex-units-from-sonarqube) |
| Dependencies | The amount of (outdated) dependencies. | ≦ 0 dependencies | count (default), percentage | maintainability | [Composer](#dependencies-from-composer), [OWASP Dependency Check](#dependencies-from-owasp-dependency-check), [npm](#dependencies-from-npm), [pip](#dependencies-from-pip) |
| Duplicated lines | The amount of lines that are duplicated. | ≦ 0 lines | count (default), percentage | maintainability | [SonarQube](#duplicated-lines-from-sonarqube) |
| Failed CI-jobs | The number of continuous integration jobs or pipelines that have failed. | ≦ 0 CI-jobs | count | ci | [Azure DevOps Server](#failed-ci-jobs-from-azure-devops-server), [GitLab](#failed-ci-jobs-from-gitlab), [Jenkins](#failed-ci-jobs-from-jenkins) |
| Issues | The number of issues. | ≦ 0 issues | count |  | [Azure DevOps Server](#issues-from-azure-devops-server), [Jira](#issues-from-jira), [Trello](#issues-from-trello) |
| Long units | The amount of units (functions, methods, files) that are too long. | ≦ 0 long units | count (default), percentage | maintainability | [SonarQube](#long-units-from-sonarqube) |
| Manual test duration | The duration of the manual test in minutes. | ≦ 0 minutes | count | test quality | [Jira](#manual-test-duration-from-jira) |
| Manual test execution | Measure the number of manual test cases that have not been tested on time. | ≦ 0 manual test cases | count | test quality | [Jira](#manual-test-execution-from-jira) |
| Many parameters | The amount of units (functions, methods, procedures) that have too many parameters. | ≦ 0 units with too many parameters | count (default), percentage | maintainability | [SonarQube](#many-parameters-from-sonarqube) |
| Merge requests | The amount of merge requests. | ≦ 0 merge requests | count (default), percentage | ci | [Azure DevOps Server](#merge-requests-from-azure-devops-server), [GitLab](#merge-requests-from-gitlab) |
| Metrics | The amount of metrics from one more quality reports, with specific states and/or tags. | ≦ 0 metrics | count (default), percentage |  | [Quality-time](#metrics-from-quality-time) |
| Missing metrics | Count the number of metrics that can be added to each report, but have not been added yet. | ≦ 0 missing metrics | count (default), percentage |  | [Quality-time](#missing-metrics-from-quality-time) |
| Performancetest duration | The duration of the performancetest in minutes. | ≧ 30 minutes | count | performance | [Performancetest-runner](#performancetest-duration-from-performancetest-runner) |
| Performancetest stability | The duration of the performancetest at which throughput or error count increases. | ≧ 100% of the minutes | percentage | performance | [Performancetest-runner](#performancetest-stability-from-performancetest-runner) |
| Scalability | The percentage of (max) users at which ramp-up of throughput breaks. | ≧ 75% of the users | percentage | performance | [Performancetest-runner](#scalability-from-performancetest-runner) |
| Security warnings | The number of security warnings about the software. | ≦ 0 security warnings | count | security | [Anchore Jenkins plugin](#security-warnings-from-anchore-jenkins-plugin), [Anchore](#security-warnings-from-anchore), [Bandit](#security-warnings-from-bandit), [Checkmarx CxSAST](#security-warnings-from-checkmarx-cxsast), [JSON file with security warnings](#security-warnings-from-json-file-with-security-warnings), [OWASP Dependency Check](#security-warnings-from-owasp-dependency-check), [OWASP ZAP](#security-warnings-from-owasp-zap), [OpenVAS](#security-warnings-from-openvas), [Pyupio Safety](#security-warnings-from-pyupio-safety), [Snyk](#security-warnings-from-snyk), [SonarQube](#security-warnings-from-sonarqube) |
| Size (LOC) | The size of the software in lines of code. | ≦ 30000 lines | count | maintainability | [SonarQube](#size-(loc)-from-sonarqube), [cloc](#size-(loc)-from-cloc) |
| Slow transactions | The number of transactions slower than their performance threshold. | ≦ 0 transactions | count | performance | [Performancetest-runner](#slow-transactions-from-performancetest-runner) |
| Source up-to-dateness | The number of days since the source was last updated. | ≦ 3 days | count | ci | [Anchore Jenkins plugin](#source-up-to-dateness-from-anchore-jenkins-plugin), [Anchore](#source-up-to-dateness-from-anchore), [Axe-core](#source-up-to-dateness-from-axe-core), [Azure DevOps Server](#source-up-to-dateness-from-azure-devops-server), [Bandit](#source-up-to-dateness-from-bandit), [Calendar date](#source-up-to-dateness-from-calendar-date), [Checkmarx CxSAST](#source-up-to-dateness-from-checkmarx-cxsast), [Cobertura Jenkins plugin](#source-up-to-dateness-from-cobertura-jenkins-plugin), [Cobertura](#source-up-to-dateness-from-cobertura), [GitLab](#source-up-to-dateness-from-gitlab), [JUnit XML report](#source-up-to-dateness-from-junit-xml-report), [JaCoCo Jenkins plugin](#source-up-to-dateness-from-jacoco-jenkins-plugin), [JaCoCo](#source-up-to-dateness-from-jacoco), [Jenkins test report](#source-up-to-dateness-from-jenkins-test-report), [Jenkins](#source-up-to-dateness-from-jenkins), [NCover](#source-up-to-dateness-from-ncover), [OWASP Dependency Check](#source-up-to-dateness-from-owasp-dependency-check), [OWASP ZAP](#source-up-to-dateness-from-owasp-zap), [OpenVAS](#source-up-to-dateness-from-openvas), [Performancetest-runner](#source-up-to-dateness-from-performancetest-runner), [Quality-time](#source-up-to-dateness-from-quality-time), [Robot Framework Jenkins plugin](#source-up-to-dateness-from-robot-framework-jenkins-plugin), [Robot Framework](#source-up-to-dateness-from-robot-framework), [SonarQube](#source-up-to-dateness-from-sonarqube), [TestNG](#source-up-to-dateness-from-testng), [Trello](#source-up-to-dateness-from-trello) |
| Source version | The version number of the source. | ≧ 1.0  | version_number | ci | [Axe-core](#source-version-from-axe-core), [Checkmarx CxSAST](#source-version-from-checkmarx-cxsast), [Cobertura](#source-version-from-cobertura), [GitLab](#source-version-from-gitlab), [Jenkins](#source-version-from-jenkins), [Jira](#source-version-from-jira), [OWASP Dependency Check](#source-version-from-owasp-dependency-check), [OWASP ZAP](#source-version-from-owasp-zap), [OpenVAS](#source-version-from-openvas), [Quality-time](#source-version-from-quality-time), [Robot Framework](#source-version-from-robot-framework), [SonarQube](#source-version-from-sonarqube), [cloc](#source-version-from-cloc) |
| Suppressed violations | The amount of violations suppressed in the source. | ≦ 0 suppressed violations | count (default), percentage | maintainability | [SonarQube](#suppressed-violations-from-sonarqube) |
| Test branch coverage | The amount of code branches not covered by tests. | ≦ 0 uncovered branches | count (default), percentage | test quality | [Cobertura Jenkins plugin](#test-branch-coverage-from-cobertura-jenkins-plugin), [Cobertura](#test-branch-coverage-from-cobertura), [JaCoCo Jenkins plugin](#test-branch-coverage-from-jacoco-jenkins-plugin), [JaCoCo](#test-branch-coverage-from-jacoco), [NCover](#test-branch-coverage-from-ncover), [SonarQube](#test-branch-coverage-from-sonarqube) |
| Test line coverage | The amount of lines of code not covered by tests. | ≦ 0 uncovered lines | count (default), percentage | test quality | [Cobertura Jenkins plugin](#test-line-coverage-from-cobertura-jenkins-plugin), [Cobertura](#test-line-coverage-from-cobertura), [JaCoCo Jenkins plugin](#test-line-coverage-from-jacoco-jenkins-plugin), [JaCoCo](#test-line-coverage-from-jacoco), [NCover](#test-line-coverage-from-ncover), [SonarQube](#test-line-coverage-from-sonarqube) |
| Tests | The amount of tests. | ≧ 0 tests | count (default), percentage | test quality | [Azure DevOps Server](#tests-from-azure-devops-server), [JUnit XML report](#tests-from-junit-xml-report), [Jenkins test report](#tests-from-jenkins-test-report), [Performancetest-runner](#tests-from-performancetest-runner), [Robot Framework Jenkins plugin](#tests-from-robot-framework-jenkins-plugin), [Robot Framework](#tests-from-robot-framework), [SonarQube](#tests-from-sonarqube), [TestNG](#tests-from-testng) |
| Unmerged branches | The number of branches that have not been merged to the default branch. | ≦ 0 branches | count | ci | [Azure DevOps Server](#unmerged-branches-from-azure-devops-server), [GitLab](#unmerged-branches-from-gitlab) |
| Unused CI-jobs | The number of continuous integration jobs that are unused. | ≦ 0 CI-jobs | count | ci | [Azure DevOps Server](#unused-ci-jobs-from-azure-devops-server), [GitLab](#unused-ci-jobs-from-gitlab), [Jenkins](#unused-ci-jobs-from-jenkins) |
| User story points | The total number of points of a selection of user stories. | ≧ 100 user story points | count | process efficiency | [Azure DevOps Server](#user-story-points-from-azure-devops-server), [Jira](#user-story-points-from-jira) |
| Velocity | The average number of user story points delivered in recent sprints. | ≧ 20 user story points per sprint | count | process efficiency | [Jira](#velocity-from-jira) |
| Violation remediation effort | The amount of effort it takes to remediate violations. | ≦ 60 minutes | count | maintainability | [SonarQube](#violation-remediation-effort-from-sonarqube) |
| Violations | The number of violations of programming rules in the software. | ≦ 0 violations | count | maintainability | [OJAudit](#violations-from-ojaudit), [SonarQube](#violations-from-sonarqube) |

## Sources

| Name | Description | Metrics |
| :--- | :---------- | :------ |
| [Anchore](https://docs.anchore.com/current/docs/using/integration/ci_cd/inline_scanning/) | Anchore image scan analysis report in JSON format. | [Source up-to-dateness](#source-up-to-dateness-from-anchore), [Security warnings](#security-warnings-from-anchore) |
| [Anchore Jenkins plugin](https://plugins.jenkins.io/anchore-container-scanner/) | A Jenkins job with an Anchore report produced by the Anchore Jenkins plugin. | [Source up-to-dateness](#source-up-to-dateness-from-anchore-jenkins-plugin), [Security warnings](#security-warnings-from-anchore-jenkins-plugin) |
| [Axe CSV](https://github.com/ICTU/axe-reports) | An Axe accessibility report in CSV format. | [Accessibility violations](#accessibility-violations-from-axe-csv) |
| [Axe-core](https://github.com/dequelabs/axe-core) | Axe is an accessibility testing engine for websites and other HTML-based user interfaces. | [Accessibility violations](#accessibility-violations-from-axe-core), [Source up-to-dateness](#source-up-to-dateness-from-axe-core), [Source version](#source-version-from-axe-core) |
| [Azure DevOps Server](https://azure.microsoft.com/en-us/services/devops/server/) | Azure DevOps Server (formerly known as Team Foundation Server) by Microsoft provides source code management, reporting, requirements management, project management, automated builds, testing and release management. | [Failed CI-jobs](#failed-ci-jobs-from-azure-devops-server), [Issues](#issues-from-azure-devops-server), [Merge requests](#merge-requests-from-azure-devops-server), [Source up-to-dateness](#source-up-to-dateness-from-azure-devops-server), [Tests](#tests-from-azure-devops-server), [Unmerged branches](#unmerged-branches-from-azure-devops-server), [Unused CI-jobs](#unused-ci-jobs-from-azure-devops-server), [User story points](#user-story-points-from-azure-devops-server) |
| [Bandit](https://github.com/PyCQA/bandit) | Bandit is a tool designed to find common security issues in Python code. | [Source up-to-dateness](#source-up-to-dateness-from-bandit), [Security warnings](#security-warnings-from-bandit) |
| Calendar date | Warn when the date is too long ago. Can be used to, for example, warn when it is time for the next security test. | [Source up-to-dateness](#source-up-to-dateness-from-calendar-date) |
| [Checkmarx CxSAST](https://www.checkmarx.com/products/static-application-security-testing/) | Static analysis software to identify security vulnerabilities in both custom code and open source components. | [Source up-to-dateness](#source-up-to-dateness-from-checkmarx-cxsast), [Source version](#source-version-from-checkmarx-cxsast), [Security warnings](#security-warnings-from-checkmarx-cxsast) |
| [Cobertura](https://cobertura.github.io/cobertura/) | Cobertura is a free Java tool that calculates the percentage of code accessed by tests. | [Source up-to-dateness](#source-up-to-dateness-from-cobertura), [Source version](#source-version-from-cobertura), [Test branch coverage](#test-branch-coverage-from-cobertura), [Test line coverage](#test-line-coverage-from-cobertura) |
| [Cobertura Jenkins plugin](https://plugins.jenkins.io/cobertura/) | Jenkins plugin for Cobertura, a free Java tool that calculates the percentage of code accessed by tests. | [Source up-to-dateness](#source-up-to-dateness-from-cobertura-jenkins-plugin), [Test branch coverage](#test-branch-coverage-from-cobertura-jenkins-plugin), [Test line coverage](#test-line-coverage-from-cobertura-jenkins-plugin) |
| [Composer](https://getcomposer.org/) | A Dependency Manager for PHP. | [Dependencies](#dependencies-from-composer) |
| [GitLab](https://gitlab.com/) | GitLab provides Git-repositories, wiki's, issue-tracking and continuous integration/continuous deployment pipelines. | [Failed CI-jobs](#failed-ci-jobs-from-gitlab), [Merge requests](#merge-requests-from-gitlab), [Source up-to-dateness](#source-up-to-dateness-from-gitlab), [Source version](#source-version-from-gitlab), [Unmerged branches](#unmerged-branches-from-gitlab), [Unused CI-jobs](#unused-ci-jobs-from-gitlab) |
| [JSON file with security warnings](https://github.com/ICTU/quality-time/blob/master/docs/USAGE.md#generic-json-for-security-warnings) | A generic vulnerability report with security warnings in JSON format. | [Security warnings](#security-warnings-from-json-file-with-security-warnings) |
| [JUnit XML report](https://junit.org) | Test reports in the JUnit XML format. | [Source up-to-dateness](#source-up-to-dateness-from-junit-xml-report), [Tests](#tests-from-junit-xml-report) |
| [JaCoCo](https://www.eclemma.org/jacoco/) | JaCoCo is an open-source tool for measuring and reporting Java code coverage. | [Source up-to-dateness](#source-up-to-dateness-from-jacoco), [Test branch coverage](#test-branch-coverage-from-jacoco), [Test line coverage](#test-line-coverage-from-jacoco) |
| [JaCoCo Jenkins plugin](https://plugins.jenkins.io/jacoco) | A Jenkins job with a JaCoCo coverage report produced by the JaCoCo Jenkins plugin. | [Source up-to-dateness](#source-up-to-dateness-from-jacoco-jenkins-plugin), [Test branch coverage](#test-branch-coverage-from-jacoco-jenkins-plugin), [Test line coverage](#test-line-coverage-from-jacoco-jenkins-plugin) |
| [Jenkins](https://jenkins.io/) | Jenkins is an open source continuous integration/continuous deployment server. | [Failed CI-jobs](#failed-ci-jobs-from-jenkins), [Source up-to-dateness](#source-up-to-dateness-from-jenkins), [Source version](#source-version-from-jenkins), [Unused CI-jobs](#unused-ci-jobs-from-jenkins) |
| [Jenkins test report](https://plugins.jenkins.io/junit) | A Jenkins job with test results. | [Source up-to-dateness](#source-up-to-dateness-from-jenkins-test-report), [Tests](#tests-from-jenkins-test-report) |
| [Jira](https://www.atlassian.com/software/jira) | Jira is a proprietary issue tracker developed by Atlassian supporting bug tracking and agile project management. | [Issues](#issues-from-jira), [Manual test duration](#manual-test-duration-from-jira), [Manual test execution](#manual-test-execution-from-jira), [Source version](#source-version-from-jira), [User story points](#user-story-points-from-jira), [Velocity](#velocity-from-jira) |
| Manual number | A manual number. | ¹ |
| [NCover](https://www.ncover.com/) | A .NET code coverage solution. | [Source up-to-dateness](#source-up-to-dateness-from-ncover), [Test branch coverage](#test-branch-coverage-from-ncover), [Test line coverage](#test-line-coverage-from-ncover) |
| [OJAudit](https://www.oracle.com/technetwork/developer-tools/jdev) | An Oracle JDeveloper program to audit Java code against JDeveloper's audit rules. | [Violations](#violations-from-ojaudit) |
| [OWASP Dependency Check](https://www.owasp.org/index.php/OWASP_Dependency_Check) | Dependency-Check is a utility that identifies project dependencies and checks if there are any known, publicly disclosed, vulnerabilities. | [Dependencies](#dependencies-from-owasp-dependency-check), [Source up-to-dateness](#source-up-to-dateness-from-owasp-dependency-check), [Source version](#source-version-from-owasp-dependency-check), [Security warnings](#security-warnings-from-owasp-dependency-check) |
| [OWASP ZAP](https://www.owasp.org/index.php/OWASP_Zed_Attack_Proxy_Project) | The OWASP Zed Attack Proxy (ZAP) can help automatically find security vulnerabilities in web applications while the application is being developed and tested. | [Source up-to-dateness](#source-up-to-dateness-from-owasp-zap), [Source version](#source-version-from-owasp-zap), [Security warnings](#security-warnings-from-owasp-zap) |
| [OpenVAS](http://www.openvas.org) | OpenVAS (Open Vulnerability Assessment System) is a software framework of several services and tools offering vulnerability scanning and vulnerability management. | [Source up-to-dateness](#source-up-to-dateness-from-openvas), [Source version](#source-version-from-openvas), [Security warnings](#security-warnings-from-openvas) |
| [Performancetest-runner](https://github.com/ICTU/performancetest-runner) | An open source tool to run performancetests and create performancetest reports. | [Performancetest duration](#performancetest-duration-from-performancetest-runner), [Performancetest stability](#performancetest-stability-from-performancetest-runner), [Scalability](#scalability-from-performancetest-runner), [Slow transactions](#slow-transactions-from-performancetest-runner), [Source up-to-dateness](#source-up-to-dateness-from-performancetest-runner), [Tests](#tests-from-performancetest-runner) |
| [Pyupio Safety](https://github.com/pyupio/safety) | Safety checks Python dependencies for known security vulnerabilities. | [Security warnings](#security-warnings-from-pyupio-safety) |
| [Quality-time](https://github.com/ICTU/quality-time) | Quality report software for software development and maintenance. | [Metrics](#metrics-from-quality-time), [Missing metrics](#missing-metrics-from-quality-time), [Source up-to-dateness](#source-up-to-dateness-from-quality-time), [Source version](#source-version-from-quality-time) |
| [Robot Framework](https://robotframework.org) | Robot Framework is a generic open source automation framework for acceptance testing, acceptance test driven development, and robotic process automation. | [Source up-to-dateness](#source-up-to-dateness-from-robot-framework), [Source version](#source-version-from-robot-framework), [Tests](#tests-from-robot-framework) |
| [Robot Framework Jenkins plugin](https://plugins.jenkins.io/robot/) | A Jenkins plugin for Robot Framework, a generic open source automation framework for acceptance testing, acceptance test driven development, and robotic process automation. | [Source up-to-dateness](#source-up-to-dateness-from-robot-framework-jenkins-plugin), [Tests](#tests-from-robot-framework-jenkins-plugin) |
| [Snyk](https://support.snyk.io/hc/en-us/articles/360003812458-Getting-started-with-the-CLI) | Snyk vulnerability report in JSON format. | [Security warnings](#security-warnings-from-snyk) |
| [SonarQube](https://www.sonarqube.org) | SonarQube is an open-source platform for continuous inspection of code quality to perform automatic reviews with static analysis of code to detect bugs, code smells, and security vulnerabilities on 20+ programming languages. | [Commented out code](#commented-out-code-from-sonarqube), [Complex units](#complex-units-from-sonarqube), [Duplicated lines](#duplicated-lines-from-sonarqube), [Size (LOC)](#size-(loc)-from-sonarqube), [Long units](#long-units-from-sonarqube), [Many parameters](#many-parameters-from-sonarqube), [Violation remediation effort](#violation-remediation-effort-from-sonarqube), [Source up-to-dateness](#source-up-to-dateness-from-sonarqube), [Source version](#source-version-from-sonarqube), [Security warnings](#security-warnings-from-sonarqube), [Suppressed violations](#suppressed-violations-from-sonarqube), [Tests](#tests-from-sonarqube), [Test branch coverage](#test-branch-coverage-from-sonarqube), [Test line coverage](#test-line-coverage-from-sonarqube), [Violations](#violations-from-sonarqube) |
| [TestNG](https://testng.org) | Test reports in the TestNG XML format. | [Source up-to-dateness](#source-up-to-dateness-from-testng), [Tests](#tests-from-testng) |
| [Trello](https://trello.com) | Trello is a collaboration tool that organizes projects into boards. | [Issues](#issues-from-trello), [Source up-to-dateness](#source-up-to-dateness-from-trello) |
| [cloc](https://github.com/AlDanial/cloc) | cloc is an open-source tool for counting blank lines, comment lines, and physical lines of source code in many programming languages. | [Size (LOC)](#size-(loc)-from-cloc), [Source version](#source-version-from-cloc) |
| [npm](https://docs.npmjs.com/) | npm is a package manager for the JavaScript programming language. | [Dependencies](#dependencies-from-npm) |
| [pip](https://pip.pypa.io/en/stable/) | pip is the package installer for Python. You can use pip to install packages from the Python Package Index and other indexes. | [Dependencies](#dependencies-from-pip) |

¹) All metrics with the count or percentage scale can be measured using the 'Manual number' source.

## Supported metric-source combinations

### Accessibility violations from Axe CSV

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Impact levels | Multiple choice | critical, minor, moderate, serious | _all impact levels_ | No | If provided, only count accessibility violations with the selected impact levels. |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an Axe report in CSV format or to a zip with Axe reports in CSV format | URL |  |  | Yes |  |
| URL to an Axe report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Axe report in CSV format. |
| Username for basic authentication | String |  |  | No |  |
| Violation types | Multiple choice | accesskeys, area-alt, aria-allowed-attr, aria-allowed-role, aria-dpub-role-fallback, aria-hidden-body, aria-hidden-focus, aria-input-field-name, aria-required-attr, aria-required-children, aria-required-parent, aria-roledescription, aria-roles, aria-toggle-field-name, aria-valid-attr, aria-valid-attr-value, audio-caption, autocomplete-valid, avoid-inline-spacing, blink, button-name, bypass, checkboxgroup, color-contrast, css-orientation-lock, definition-list, dlitem, document-title, duplicate-id, duplicate-id-active, duplicate-id-aria, empty-heading, focus-order-semantics, form-field-multiple-labels, frame-tested, frame-title, frame-title-unique, heading-order, hidden-content, html-has-lang, html-lang-valid, html-xml-lang-mismatch, image-alt, image-redundant-alt, input-button-name, input-image-alt, label, label-content-name-mismatch, label-title-only, landmark-banner-is-top-level, landmark-complementary-is-top-level, landmark-contentinfo-is-top-level, landmark-main-is-top-level, landmark-no-duplicate-banner, landmark-no-duplicate-contentinfo, landmark-one-main, landmark-unique, layout-table, link-in-text-block, link-name, list, listitem, marquee, meta-refresh, meta-viewport, meta-viewport-large, object-alt, p-as-heading, page-has-heading-one, radiogroup, region, role-img-alt, scope-attr-valid, scrollable-region-focusable, server-side-image-map, skip-link, tabindex, table-duplicate-name, table-fake-caption, td-has-header, td-headers-attr, th-has-data-cells, valid-lang, video-caption, video-description | _all violation types_ | No | [https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md) |

### Accessibility violations from Axe-core

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Impact levels | Multiple choice | critical, minor, moderate, serious | _all impact levels_ | No | If provided, only count accessibility violations with the selected impact levels. |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Result types | Multiple choice | inapplicable, incomplete, passes, violations | violations | No | Limit which result types to count. |
| Tags to ignore (regular expressions or tags) | Multiple choice with addition |  |  | No | Tags to ignore can be specified by tag or by regular expression. |
| Tags to include (regular expressions or tags) | Multiple choice with addition |  |  | No | Tags to include can be specified by tag or by regular expression. |
| URL to an Axe-core report in JSON format or to a zip with Axe-core reports in JSON format | URL |  |  | Yes |  |
| URL to an Axe-core report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Axe-core report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Commented out code from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

| Configuration | Value |
| :------------ | :---- |
| Rules used to detect commented out code | abap:S125, apex:S125, c:CommentedCode, cpp:CommentedCode, csharpsquid:S125, flex:CommentedCode, java:S125, javascript:CommentedCode, javascript:S125, kotlin:S125, objc:CommentedCode, php:S125, plsql:S125, python:S125, scala:S125, squid:CommentedOutCodeLine, swift:S125, typescript:S125, Web:AvoidCommentedOutCodeCheck, xml:S125 |

### Complex units from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

| Configuration | Value |
| :------------ | :---- |
| Rules used to detect complex units | csharpsquid:S1541, csharpsquid:S3776, flex:FunctionComplexity, go:S3776, java:S1541, javascript:FunctionComplexity, javascript:S1541, javascript:S3776, kotlin:S3776, php:S1541, php:S3776, python:FunctionComplexity, python:S3776, ruby:S3776, scala:S3776, squid:MethodCyclomaticComplexity, squid:S3776, typescript:S1541, typescript:S3776, vbnet:S1541, vbnet:S3776 |

### Dependencies from Composer

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Latest version statuses | Multiple choice | safe update possible, unknown, up-to-date, update possible | _all statuses_ | No | Limit which latest version statuses to show. The status 'safe update possible' means that based on semantic versioning the update should be backwards compatible. |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Composer 'outdated' report in JSON format or to a zip with Composer 'outdated' reports in JSON format | URL |  |  | Yes | [https://getcomposer.org/doc/03-cli.md#outdated](https://getcomposer.org/doc/03-cli.md#outdated) |
| URL to a Composer 'outdated' report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Composer 'outdated' report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Dependencies from npm

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a npm 'outdated' report in JSON format or to a zip with npm 'outdated' reports in JSON format | URL |  |  | Yes | [https://docs.npmjs.com/cli-commands/outdated.html](https://docs.npmjs.com/cli-commands/outdated.html) |
| URL to a npm 'outdated' report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the npm 'outdated' report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Dependencies from OWASP Dependency Check

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format | URL |  |  | Yes |  |
| URL to an OWASP Dependency Check report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OWASP Dependency Check report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Dependencies from pip

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a pip 'outdated' report in JSON format or to a zip with pip 'outdated' reports in JSON format | URL |  |  | Yes | [https://pip.pypa.io/en/stable/reference/pip_list/](https://pip.pypa.io/en/stable/reference/pip_list/) |
| URL to a pip 'outdated' report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the pip 'outdated' report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Duplicated lines from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Failed CI-jobs from Azure DevOps Server

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Failure types | Multiple choice | canceled, failed, no result, partially succeeded | _all failure types_ | No | Limit which failure types to count as failed. |
| Pipelines to ignore (regular expressions or pipeline names) | Multiple choice with addition |  |  | No | Pipelines to ignore can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders. |
| Pipelines to include (regular expressions or pipeline names) | Multiple choice with addition |  |  | No | Pipelines to include can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders. |
| Private token | Password |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) |
| URL including organization and project | URL |  |  | Yes | URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'. |

### Failed CI-jobs from Jenkins

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Failure types | Multiple choice | Aborted, Failure, Not built, Unstable | _all failure types_ | No | Limit which failure types to count as failed. |
| Jobs to ignore (regular expressions or job names) | Multiple choice with addition |  |  | No | Jobs to ignore can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs. |
| Jobs to include (regular expressions or job names) | Multiple choice with addition |  |  | No | Jobs to include can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs. |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL | URL |  |  | Yes | URL of the Jenkins instance, with port if necessary, but without path. For example, 'https://jenkins.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Failed CI-jobs from GitLab

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branches and tags to ignore (regular expressions, branch names or tag names) | Multiple choice with addition |  |  | No | [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/) |
| Failure types | Multiple choice | canceled, failed, skipped | _all failure types_ | No | Limit which failure types to count as failed. |
| GitLab instance URL | URL |  |  | Yes | URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'. |
| Jobs to ignore (regular expressions or job names) | Multiple choice with addition |  |  | No | Jobs to ignore can be specified by job name or by regular expression. |
| Private token (with read_api scope) | Password |  |  | No | [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) |
| Project (name with namespace or id) | String |  |  | Yes | [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/) |

### Issues from Azure DevOps Server

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Issue query in WIQL (Work Item Query Language) | String |  |  | Yes | [https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops) |
| Private token | Password |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) |
| URL including organization and project | URL |  |  | Yes | URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'. |

### Issues from Jira

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Issue query in JQL (Jira Query Language) | String |  |  | Yes | [https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html](https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html) |
| Password for basic authentication | Password |  |  | No |  |
| URL | URL |  |  | Yes | URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Issues from Trello

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| API key | String |  |  | No | [https://trello.com/app-key](https://trello.com/app-key) |
| Board (title or id) | String |  |  | Yes | [https://trello.com/1/members/me/boards?fields=name](https://trello.com/1/members/me/boards?fields=name) |
| Cards to count | Multiple choice | inactive, overdue | _all cards_ | No |  |
| Lists to ignore (title or id) | Multiple choice with addition |  |  | No |  |
| Number of days without activity after which to consider cards inactive | Integer |  | 30 | No |  |
| Token | String |  |  | No | [https://trello.com/app-key](https://trello.com/app-key) |
| URL | URL |  | https://trello.com | Yes |  |

### Size (LOC) from cloc

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Languages to ignore (regular expressions or language names) | Multiple choice with addition |  |  | No | [https://github.com/AlDanial/cloc#recognized-languages-](https://github.com/AlDanial/cloc#recognized-languages-) |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a cloc report in JSON format or to a zip with cloc reports in JSON format | URL |  |  | Yes |  |
| URL to a cloc report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the cloc report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Size (LOC) from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Languages to ignore (regular expressions or language names) | Multiple choice with addition |  |  | No | [https://docs.sonarqube.org/latest/analysis/languages/overview/](https://docs.sonarqube.org/latest/analysis/languages/overview/) |
| Lines to count | Single choice | all lines, lines with code | lines with code | No | Either count all lines including lines with comments or only count lines with code, excluding comments. Note: it's possible to ignore specific languages only when counting lines with code. This is a SonarQube limitation. |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Long units from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

| Configuration | Value |
| :------------ | :---- |
| Rules used to detect long units | abap:S104, c:FileLoc, cpp:FileLoc, csharpsquid:S104, csharpsquid:S138, flex:S138, go:S104, go:S138, java:S138, javascript:S104, javascript:S138, kotlin:S104, kotlin:S138, objc:FileLoc, php:S104, php:S138, php:S2042, Pylint:R0915, python:S104, ruby:S104, ruby:S138, scala:S104, scala:S138, squid:S00104, squid:S1188, squid:S138, squid:S2972, swift:S104, typescript:S104, typescript:S138, vbnet:S104, vbnet:S138, Web:FileLengthCheck, Web:LongJavaScriptCheck |

### Manual test duration from Jira

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Issue query in JQL (Jira Query Language) | String |  |  | Yes | [https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html](https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html) |
| Manual test duration field (name or id) | String |  |  | Yes | [https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html) |
| Password for basic authentication | Password |  |  | No |  |
| URL | URL |  |  | Yes | URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Manual test execution from Jira

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Default expected manual test execution frequency (days) | Integer |  | 21 | Yes | Specify how often the manual tests should be executed. For example, if the sprint length is three weeks, manual tests should be executed at least once every 21 days. |
| Issue query in JQL (Jira Query Language) | String |  |  | Yes | [https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html](https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html) |
| Manual test execution frequency field (name or id) | String |  |  | No | [https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html) |
| Password for basic authentication | Password |  |  | No |  |
| URL | URL |  |  | Yes | URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Many parameters from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

| Configuration | Value |
| :------------ | :---- |
| Rules used to detect units with many parameters | c:S107, cpp:S107, csharpsquid:S107, csharpsquid:S2436, flex:S107, java:S107, javascript:ExcessiveParameterList, javascript:S107, objc:S107, php:S107, plsql:PlSql.FunctionAndProcedureExcessiveParameters, python:S107, squid:S00107, tsql:S107, typescript:S107 |

### Merge requests from Azure DevOps Server

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Merge request states | Multiple choice | abandoned, active, completed, not set | _all states_ | No | Limit which merge request states to count. |
| Minimum number of upvotes | Integer |  | 0 | No | Only count merge requests with fewer than the minimum number of upvotes. |
| Private token | Password |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) |
| Repository (name or id) | String |  |  | No |  |
| Target branches to include (regular expressions or branch names) | Multiple choice with addition |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops) |
| URL including organization and project | URL |  |  | Yes | URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'. |

### Merge requests from GitLab

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| GitLab instance URL | URL |  |  | Yes | URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'. |
| Merge request states | Multiple choice | closed, locked, merged, opened | _all states_ | No | Limit which merge request states to count. |
| Minimum number of upvotes | Integer |  | 0 | No | Only count merge requests with fewer than the minimum number of upvotes. |
| Private token (with read_api scope) | Password |  |  | No | [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) |
| Project (name with namespace or id) | String |  |  | Yes | [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/) |
| Target branches to include (regular expressions or branch names) | Multiple choice with addition |  |  | No | [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/) |

### Metrics from Quality-time

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Metric statuses | Multiple choice | near target met (yellow), target met (green), target not met (red), technical debt target met (grey), unknown (white) | _all metric statuses_ | No |  |
| Metric types | Multiple choice | Accessibility violations, Commented out code, Complex units, Dependencies, Duplicated lines, Failed CI-jobs, Issues, Long units, Manual test duration, Manual test execution, Many parameters, Merge requests, Metrics, Missing metrics, Performancetest duration, Performancetest stability, Ready user story points, Scalability, Security warnings, Size (LOC), Slow transactions, Source up-to-dateness, Source version, Suppressed violations, Test branch coverage, Test line coverage, Tests, Unmerged branches, Unused CI-jobs, User story points, Velocity, Violation remediation effort, Violations | _all metric types_ | No | If provided, only count metrics with the selected metric types. |
| Quality-time URL | URL |  |  | Yes | URL of the Quality-time instance, with port if necessary, but without path. For example, 'https://quality-time.example.org'. |
| Report names or identifiers | Multiple choice with addition |  |  | No |  |
| Source types | Multiple choice | Anchore, Anchore Jenkins plugin, Axe CSV, Axe-core, Azure DevOps Server, Bandit, Calendar date, Checkmarx CxSAST, Cobertura, Cobertura Jenkins plugin, Composer, GitLab, JSON file with security warnings, JUnit XML report, JaCoCo, JaCoCo Jenkins plugin, Jenkins, Jenkins test report, Jira, Manual number, NCover, OJAudit, OWASP Dependency Check, OWASP ZAP, OpenVAS, Performancetest-runner, Pyupio Safety, Quality-time, Robot Framework, Robot Framework Jenkins plugin, Snyk, SonarQube, TestNG, Trello, cloc, npm, pip | _all source types_ | No | If provided, only count metrics with one or more sources of the selected source types. |
| Tags | Multiple choice with addition |  |  | No | If provided, only count metrics with one ore more of the given tags. |

### Missing metrics from Quality-time

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Quality-time URL | URL |  |  | Yes | URL of the Quality-time instance, with port if necessary, but without path. For example, 'https://quality-time.example.org'. |
| Report names or identifiers | Multiple choice with addition |  |  | No |  |

### Performancetest duration from Performancetest-runner

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Performancetest stability from Performancetest-runner

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Violation remediation effort from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| Types of effort | Multiple choice | effort to fix all bug issues, effort to fix all code smells, effort to fix all vulnerabilities | _all effort types_ | No | [https://docs.sonarqube.org/latest/user-guide/metric-definitions/](https://docs.sonarqube.org/latest/user-guide/metric-definitions/) |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Scalability from Performancetest-runner

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Slow transactions from Performancetest-runner

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Thresholds | Multiple choice | high, warning | _all thresholds_ | No | If provided, only count transactions that surpass the selected thresholds. |
| Transactions to ignore (regular expressions or transaction names) | Multiple choice with addition |  |  | No | Transactions to ignore can be specified by transaction name or by regular expression. |
| Transactions to include (regular expressions or transaction names) | Multiple choice with addition |  |  | No | Transactions to include can be specified by transaction name or by regular expression. |
| URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Anchore

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an Anchore details report in JSON format or to a zip with Anchore details reports in JSON format | URL |  |  | Yes |  |
| URL to an Anchore vulnerability report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Anchore vulnerability report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Anchore Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with an Anchore report generated by the Anchore plugin. For example, 'http://jenkins.example.org/job/anchore' or http://jenkins.example.org/job/anchore/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Axe-core

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an Axe-core report in JSON format or to a zip with Axe-core reports in JSON format | URL |  |  | Yes |  |
| URL to an Axe-core report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Axe-core report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Azure DevOps Server

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch | String |  | master | No |  |
| File or folder path | String |  |  | No | Use the date and time the path was last changed to determine the up-to-dateness. Note that if a pipeline is specified, the pipeline is used to determine the up-to-dateness, and the path is ignored. |
| Pipelines to ignore (regular expressions or pipeline names) | Multiple choice with addition |  |  | No | Pipelines to ignore can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders. |
| Pipelines to include (regular expressions or pipeline names) | Multiple choice with addition |  |  | No | Pipelines to include can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders. |
| Private token | Password |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) |
| Repository (name or id) | String |  |  | No |  |
| URL including organization and project | URL |  |  | Yes | URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'. |

### Source up-to-dateness from Bandit

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Bandit report in JSON format or to a zip with Bandit reports in JSON format | URL |  |  | Yes |  |
| URL to a Bandit report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Bandit report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Calendar date

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Date | Date |  | 2021-01-01 | Yes |  |

### Source up-to-dateness from Cobertura

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Cobertura report in XML format or to a zip with Cobertura reports in XML format | URL |  |  | Yes |  |
| URL to a Cobertura report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Cobertura report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Cobertura Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a coverage report generated by the Cobertura plugin. For example, 'http://jenkins.example.org/job/cobertura' or http://jenkins.example.org/job/cobertura/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Checkmarx CxSAST

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | Yes |  |
| Project (name or id) | String |  |  | Yes |  |
| URL | URL |  |  | Yes | URL of the Checkmarx instance, with port if necessary, but without path. For example 'https://checkmarx.example.org'. |
| Username for basic authentication | String |  |  | Yes |  |

### Source up-to-dateness from GitLab

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch | String |  | master | No | [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/) |
| File or folder path | String |  |  | Yes | [https://docs.gitlab.com/ee/api/repository_files.html](https://docs.gitlab.com/ee/api/repository_files.html) |
| GitLab instance URL | URL |  |  | Yes | URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'. |
| Private token (with read_api scope) | Password |  |  | No | [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) |
| Project (name with namespace or id) | String |  |  | Yes | [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/) |

### Source up-to-dateness from JaCoCo

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format | URL |  |  | Yes |  |
| URL to a JaCoCo report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the JaCoCo report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from JaCoCo Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a coverage report generated by the JaCoCo plugin. For example, 'http://jenkins.example.org/job/jacoco' or http://jenkins.example.org/job/jacoco/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Jenkins

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Build result types | Multiple choice | Aborted, Failure, Not built, Success, Unstable | _all result types_ | No | Limit which build result types to include. |
| Jobs to ignore (regular expressions or job names) | Multiple choice with addition |  |  | No | Jobs to ignore can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs. |
| Jobs to include (regular expressions or job names) | Multiple choice with addition |  |  | No | Jobs to include can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs. |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL | URL |  |  | Yes | URL of the Jenkins instance, with port if necessary, but without path. For example, 'https://jenkins.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Jenkins test report

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a test report generated by the JUnit plugin. For example, 'http://jenkins.example.org/job/test' or http://jenkins.example.org/job/test/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from JUnit XML report

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a JUnit report in XML format or to a zip with JUnit reports in XML format | URL |  |  | Yes |  |
| URL to a JUnit report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the JUnit report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from NCover

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a NCover report in HTML format or to a zip with NCover reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Robot Framework

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Robot Framework report in XML format or to a zip with Robot Framework reports in XML format | URL |  |  | Yes |  |
| URL to a Robot Framework report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Robot Framework report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from OpenVAS

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an OpenVAS report in XML format or to a zip with OpenVAS reports in XML format | URL |  |  | Yes |  |
| URL to an OpenVAS report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OpenVAS report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from OWASP Dependency Check

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format | URL |  |  | Yes |  |
| URL to an OWASP Dependency Check report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OWASP Dependency Check report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from OWASP ZAP

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an OWASP ZAP report in XML format or to a zip with OWASP ZAP reports in XML format | URL |  |  | Yes |  |
| URL to an OWASP ZAP report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OWASP ZAP report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Performancetest-runner

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Quality-time

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Quality-time URL | URL |  |  | Yes | URL of the Quality-time instance, with port if necessary, but without path. For example, 'https://quality-time.example.org'. |
| Report names or identifiers | Multiple choice with addition |  |  | No |  |

### Source up-to-dateness from Robot Framework Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a test report generated by the Robot Framework plugin. For example, 'http://jenkins.example.org/job/robot' or http://jenkins.example.org/job/robot/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Source up-to-dateness from TestNG

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a TestNG report in XML format or to a zip with TestNG reports in XML format | URL |  |  | Yes |  |
| URL to a TestNG report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the TestNG report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source up-to-dateness from Trello

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| API key | String |  |  | No | [https://trello.com/app-key](https://trello.com/app-key) |
| Board (title or id) | String |  |  | Yes | [https://trello.com/1/members/me/boards?fields=name](https://trello.com/1/members/me/boards?fields=name) |
| Lists to ignore (title or id) | Multiple choice with addition |  |  | No |  |
| Token | String |  |  | No | [https://trello.com/app-key](https://trello.com/app-key) |
| URL | URL |  | https://trello.com | Yes |  |

### Source version from Axe-core

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an Axe-core report in JSON format or to a zip with Axe-core reports in JSON format | URL |  |  | Yes |  |
| URL to an Axe-core report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Axe-core report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Source version from cloc

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a cloc report in JSON format or to a zip with cloc reports in JSON format | URL |  |  | Yes |  |
| URL to a cloc report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the cloc report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Source version from Cobertura

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Cobertura report in XML format or to a zip with Cobertura reports in XML format | URL |  |  | Yes |  |
| URL to a Cobertura report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Cobertura report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source version from Checkmarx CxSAST

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | Yes |  |
| URL | URL |  |  | Yes | URL of the Checkmarx instance, with port if necessary, but without path. For example 'https://checkmarx.example.org'. |
| Username for basic authentication | String |  |  | Yes |  |

### Source version from GitLab

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| GitLab instance URL | URL |  |  | Yes | URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'. |
| Private token (with read_api scope) | Password |  |  | No | [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) |

### Source version from Jenkins

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL | URL |  |  | Yes | URL of the Jenkins instance, with port if necessary, but without path. For example, 'https://jenkins.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Source version from Jira

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| URL | URL |  |  | Yes | URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Source version from OpenVAS

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an OpenVAS report in XML format or to a zip with OpenVAS reports in XML format | URL |  |  | Yes |  |
| URL to an OpenVAS report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OpenVAS report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source version from OWASP Dependency Check

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format | URL |  |  | Yes |  |
| URL to an OWASP Dependency Check report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OWASP Dependency Check report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source version from OWASP ZAP

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to an OWASP ZAP report in XML format or to a zip with OWASP ZAP reports in XML format | URL |  |  | Yes |  |
| URL to an OWASP ZAP report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OWASP ZAP report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source version from Quality-time

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Quality-time URL | URL |  |  | Yes | URL of the Quality-time instance, with port if necessary, but without path. For example, 'https://quality-time.example.org'. |

### Source version from Robot Framework

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Robot Framework report in XML format or to a zip with Robot Framework reports in XML format | URL |  |  | Yes |  |
| URL to a Robot Framework report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Robot Framework report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Source version from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Security warnings from Anchore

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Severities | Multiple choice | Critical, High, Low, Medium, Negligible, Unknown | _all severities_ | No | If provided, only count security warnings with the selected severities. |
| URL to an Anchore vulnerability report in JSON format or to a zip with Anchore vulnerability reports in JSON format | URL |  |  | Yes |  |
| URL to an Anchore vulnerability report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Anchore vulnerability report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from Anchore Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| Severities | Multiple choice | Critical, High, Low, Medium, Negligible, Unknown | _all severities_ | No | If provided, only count security warnings with the selected severities. |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with an Anchore report generated by the Anchore plugin. For example, 'http://jenkins.example.org/job/anchore' or http://jenkins.example.org/job/anchore/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from Bandit

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Confidence levels | Multiple choice | high, low, medium | _all confidence levels_ | No | If provided, only count security warnings with the selected confidence levels. |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Severities | Multiple choice | high, low, medium | _all severities_ | No | If provided, only count security warnings with the selected severities. |
| URL to a Bandit report in JSON format or to a zip with Bandit reports in JSON format | URL |  |  | Yes |  |
| URL to a Bandit report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Bandit report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from Checkmarx CxSAST

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | Yes |  |
| Project (name or id) | String |  |  | Yes |  |
| Severities | Multiple choice | high, info, low, medium | _all severities_ | No | If provided, only count security warnings with the selected severities. |
| URL | URL |  |  | Yes | URL of the Checkmarx instance, with port if necessary, but without path. For example 'https://checkmarx.example.org'. |
| Username for basic authentication | String |  |  | Yes |  |

### Security warnings from OpenVAS

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Severities | Multiple choice | high, log, low, medium | _all severities_ | No | If provided, only count security warnings with the selected severities. |
| URL to an OpenVAS report in XML format or to a zip with OpenVAS reports in XML format | URL |  |  | Yes |  |
| URL to an OpenVAS report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OpenVAS report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from OWASP Dependency Check

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Severities | Multiple choice | critical, high, low, medium | _all severities_ | No | If provided, only count security warnings with the selected severities. |
| URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format | URL |  |  | Yes |  |
| URL to an OWASP Dependency Check report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OWASP Dependency Check report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from OWASP ZAP

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Count alert types or alert instances | Single choice | alert instances, alert types | alert instances | No | Determine whether to count each alert type in the OWASP ZAP report as a security warning or to count each alert instance (URL). |
| Parts of URLs to ignore (regular expressions) | Multiple choice with addition |  |  | No | Parts of URLs to ignore can be specified by regular expression. The parts of URLs that match one or more of the regular expressions are removed. If, after applying the regular expressions, multiple warnings are the same only one is reported. |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Risks | Multiple choice | high, informational, low, medium | _all risks_ | No | If provided, only count security warnings with the selected risks. |
| URL to an OWASP ZAP report in XML format or to a zip with OWASP ZAP reports in XML format | URL |  |  | Yes |  |
| URL to an OWASP ZAP report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OWASP ZAP report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from Pyupio Safety

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Safety report in JSON format or to a zip with Safety reports in JSON format | URL |  |  | Yes |  |
| URL to a Safety report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Safety report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from Snyk

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Severities | Multiple choice | high, low, medium | _all severities_ | No | If provided, only count security warnings with the selected severities. |
| URL to a Snyk vulnerability report in JSON format or to a zip with Snyk vulnerability reports in JSON format | URL |  |  | Yes |  |
| URL to a Snyk vulnerability report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Snyk vulnerability report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from JSON file with security warnings

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Severities | Multiple choice | high, low, medium | _all severities_ | No | If provided, only count security warnings with the selected severities. |
| URL to a generic vulnerability report in JSON format or to a zip with generic vulnerability reports in JSON format | URL |  |  | Yes |  |
| URL to a generic vulnerability report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the generic vulnerability report in JSON format. |
| Username for basic authentication | String |  |  | No |  |

### Security warnings from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| Security hotspot review priorities | Multiple choice | high, low, medium | _all review priorities_ | No | [https://docs.sonarqube.org/latest/user-guide/security-hotspots/](https://docs.sonarqube.org/latest/user-guide/security-hotspots/) |
| Security issue types (measuring security hotspots requires SonarQube 8.2 or newer) | Multiple choice | security_hotspot, vulnerability | vulnerability | No | [https://docs.sonarqube.org/latest/user-guide/rules/](https://docs.sonarqube.org/latest/user-guide/rules/) |
| Severities | Multiple choice | blocker, critical, info, major, minor | _all severities_ | No | [https://docs.sonarqube.org/latest/user-guide/issues/](https://docs.sonarqube.org/latest/user-guide/issues/) |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Suppressed violations from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| Severities | Multiple choice | blocker, critical, info, major, minor | _all severities_ | No | [https://docs.sonarqube.org/latest/user-guide/issues/](https://docs.sonarqube.org/latest/user-guide/issues/) |
| Types | Multiple choice | bug, code_smell, vulnerability | _all types_ | No | [https://docs.sonarqube.org/latest/user-guide/rules/](https://docs.sonarqube.org/latest/user-guide/rules/) |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

| Configuration | Value |
| :------------ | :---- |
| Rules used to detect suppressed violations | csharpsquid:S1309, java:NoSonar, java:S1309, java:S1310, java:S1315, php:NoSonar, Pylint:I0011, Pylint:I0020, squid:NoSonar, squid:S1309, squid:S1310, squid:S1315 |

### Tests from Azure DevOps Server

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Names of test runs to include (regular expressions or test run names) | Multiple choice with addition |  |  | No | Limit which test runs to include by test run name. |
| Private token | Password |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) |
| States of the test runs to include | Multiple choice | aborted, completed, in progress, not started | _all test run states_ | No | Limit which test runs to include by test run state. |
| Test results | Multiple choice | failed, incomplete, not applicable, passed | _all test results_ | No | Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. |
| URL including organization and project | URL |  |  | Yes | URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'. |

### Tests from Jenkins test report

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| Test results | Multiple choice | failed, passed, skipped | _all test results_ | No | Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a test report generated by the JUnit plugin. For example, 'http://jenkins.example.org/job/test' or http://jenkins.example.org/job/test/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Tests from JUnit XML report

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Test results | Multiple choice | errored, failed, passed, skipped | _all test results_ | No | Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. |
| URL to a JUnit report in XML format or to a zip with JUnit reports in XML format | URL |  |  | Yes |  |
| URL to a JUnit report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the JUnit report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Tests from Performancetest-runner

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Test results | Multiple choice | failed, success | _all test results_ | No | Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. |
| Transactions to ignore (regular expressions or transaction names) | Multiple choice with addition |  |  | No | Transactions to ignore can be specified by transaction name or by regular expression. |
| Transactions to include (regular expressions or transaction names) | Multiple choice with addition |  |  | No | Transactions to include can be specified by transaction name or by regular expression. |
| URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Tests from Robot Framework

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Test results | Multiple choice | fail, pass, skip | _all test results_ | No | Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. |
| URL to a Robot Framework report in XML format or to a zip with Robot Framework reports in XML format | URL |  |  | Yes |  |
| URL to a Robot Framework report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Robot Framework report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Tests from Robot Framework Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| Test results | Multiple choice | fail, pass | _all test results_ | No | Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a test report generated by the Robot Framework plugin. For example, 'http://jenkins.example.org/job/robot' or http://jenkins.example.org/job/robot/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Tests from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| Test results | Multiple choice | errored, failed, passed, skipped | _all test results_ | No | Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Tests from TestNG

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Test results | Multiple choice | failed, ignored, passed, skipped | _all test results_ | No | Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. |
| URL to a TestNG report in XML format or to a zip with TestNG reports in XML format | URL |  |  | Yes |  |
| URL to a TestNG report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the TestNG report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Test branch coverage from Cobertura

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Cobertura report in XML format or to a zip with Cobertura reports in XML format | URL |  |  | Yes |  |
| URL to a Cobertura report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Cobertura report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Test branch coverage from Cobertura Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a coverage report generated by the Cobertura plugin. For example, 'http://jenkins.example.org/job/cobertura' or http://jenkins.example.org/job/cobertura/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Test branch coverage from JaCoCo

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format | URL |  |  | Yes |  |
| URL to a JaCoCo report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the JaCoCo report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Test branch coverage from JaCoCo Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a coverage report generated by the JaCoCo plugin. For example, 'http://jenkins.example.org/job/jacoco' or http://jenkins.example.org/job/jacoco/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Test branch coverage from NCover

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a NCover report in HTML format or to a zip with NCover reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Test branch coverage from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Test line coverage from Cobertura

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a Cobertura report in XML format or to a zip with Cobertura reports in XML format | URL |  |  | Yes |  |
| URL to a Cobertura report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the Cobertura report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Test line coverage from Cobertura Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a coverage report generated by the Cobertura plugin. For example, 'http://jenkins.example.org/job/cobertura' or http://jenkins.example.org/job/cobertura/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Test line coverage from JaCoCo

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format | URL |  |  | Yes |  |
| URL to a JaCoCo report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the JaCoCo report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Test line coverage from JaCoCo Jenkins plugin

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL to Jenkins job | URL |  |  | Yes | URL to a Jenkins job with a coverage report generated by the JaCoCo plugin. For example, 'http://jenkins.example.org/job/jacoco' or http://jenkins.example.org/job/jacoco/job/master' in case of a pipeline job. |
| Username for basic authentication | String |  |  | No |  |

### Test line coverage from NCover

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| URL to a NCover report in HTML format or to a zip with NCover reports in HTML format | URL |  |  | Yes |  |
| Username for basic authentication | String |  |  | No |  |

### Test line coverage from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |

### Unmerged branches from Azure DevOps Server

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branches to ignore (regular expressions or branch names) | Multiple choice with addition |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops) |
| Number of days since last commit after which to consider branches inactive | Integer |  | 7 | No |  |
| Private token | Password |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) |
| Repository (name or id) | String |  |  | No |  |
| URL including organization and project | URL |  |  | Yes | URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'. |

### Unmerged branches from GitLab

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branches to ignore (regular expressions or branch names) | Multiple choice with addition |  |  | No | [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/) |
| GitLab instance URL | URL |  |  | Yes | URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'. |
| Number of days since last commit after which to consider branches inactive | Integer |  | 7 | No |  |
| Private token (with read_api scope) | Password |  |  | No | [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) |
| Project (name with namespace or id) | String |  |  | Yes | [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/) |

### Unused CI-jobs from Azure DevOps Server

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Number of days since last build after which to consider pipelines inactive | Integer |  | 21 | No |  |
| Pipelines to ignore (regular expressions or pipeline names) | Multiple choice with addition |  |  | No | Pipelines to ignore can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders. |
| Pipelines to include (regular expressions or pipeline names) | Multiple choice with addition |  |  | No | Pipelines to include can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders. |
| Private token | Password |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) |
| URL including organization and project | URL |  |  | Yes | URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'. |

### Unused CI-jobs from GitLab

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branches and tags to ignore (regular expressions, branch names or tag names) | Multiple choice with addition |  |  | No | [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/) |
| GitLab instance URL | URL |  |  | Yes | URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'. |
| Jobs to ignore (regular expressions or job names) | Multiple choice with addition |  |  | No | Jobs to ignore can be specified by job name or by regular expression. |
| Number of days without builds after which to consider CI-jobs unused. | Integer |  | 90 | No |  |
| Private token (with read_api scope) | Password |  |  | No | [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) |
| Project (name with namespace or id) | String |  |  | Yes | [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/) |

### Unused CI-jobs from Jenkins

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Jobs to ignore (regular expressions or job names) | Multiple choice with addition |  |  | No | Jobs to ignore can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs. |
| Jobs to include (regular expressions or job names) | Multiple choice with addition |  |  | No | Jobs to include can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs. |
| Number of days without builds after which to consider CI-jobs unused. | Integer |  | 90 | No |  |
| Password or API token for basic authentication | Password |  |  | No | [https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients](https://wiki.jenkins.io/display/JENKINS/Authenticating+scripted+clients) |
| URL | URL |  |  | Yes | URL of the Jenkins instance, with port if necessary, but without path. For example, 'https://jenkins.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### User story points from Azure DevOps Server

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Issue query in WIQL (Work Item Query Language) | String |  |  | Yes | [https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops) |
| Private token | Password |  |  | No | [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) |
| URL including organization and project | URL |  |  | Yes | URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'. |

### User story points from Jira

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Issue query in JQL (Jira Query Language) | String |  |  | Yes | [https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html](https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html) |
| Password for basic authentication | Password |  |  | No |  |
| Story points field (name or id) | String |  | Story Points | Yes | [https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html) |
| URL | URL |  |  | Yes | URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Velocity from Jira

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Board (name or id) | String |  |  | Yes | [https://support.atlassian.com/jira-software-cloud/docs/what-is-a-jira-software-board/](https://support.atlassian.com/jira-software-cloud/docs/what-is-a-jira-software-board/) |
| Number of sprints to base velocity on | Integer |  | 3 | Yes |  |
| Password for basic authentication | Password |  |  | No |  |
| Type of velocity | Single choice | committed points, completed points, completed points minus committed points | completed points | Yes | Whether to report the amount of story points committed to, the amount of story points actually completed, or the difference between the two. |
| URL | URL |  |  | Yes | URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'. |
| Username for basic authentication | String |  |  | No |  |

### Violations from OJAudit

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Password for basic authentication | Password |  |  | No |  |
| Private token | Password |  |  | No |  |
| Severities | Multiple choice | advisory, error, exception, incomplete, warning | _all severities_ | No | If provided, only count violations with the selected severities. |
| URL to an OJAudit report in XML format or to a zip with OJAudit reports in XML format | URL |  |  | Yes |  |
| URL to an OJAudit report in a human readable format | String |  |  | No | If provided, users clicking the source URL will visit this URL instead of the OJAudit report in XML format. |
| Username for basic authentication | String |  |  | No |  |

### Violations from SonarQube

| Parameter | Type | Values | Default value | Mandatory | Help |
| :-------- | :--- | :----- | :------------ | :-------- | :--- |
| Branch (only supported by commercial SonarQube editions) | String |  | master | No | [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/) |
| Private token | Password |  |  | No | [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/) |
| Project key | String |  |  | Yes | The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right. |
| Severities | Multiple choice | blocker, critical, info, major, minor | _all severities_ | No | [https://docs.sonarqube.org/latest/user-guide/issues/](https://docs.sonarqube.org/latest/user-guide/issues/) |
| Types | Multiple choice | bug, code_smell, vulnerability | _all types_ | No | [https://docs.sonarqube.org/latest/user-guide/rules/](https://docs.sonarqube.org/latest/user-guide/rules/) |
| URL | URL |  |  | Yes | URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'. |
