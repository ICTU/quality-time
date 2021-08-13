# *Quality-time* metrics and sources

This is an overview of all [metrics](#metrics) that *Quality-time* can measure and all [sources](#sources) that *Quality-time* can use to measure the metrics. For each [supported combination of metric and source](#metric-source-combinations), the parameters that can be used to configure the source are listed.

## Metrics

This is an overview of all the metrics that *Quality-time* can measure. For each metric, the default target, the supported scales, and the default tags are given. In addition, the sources that can be used to measure the metric are listed.

### Accessibility violations

The number of accessibility violations in the web user interface of the software.

Default target
: ≦ 0 violations

Scales
: count

Default tags
: accessibility

```{admonition} Supporting sources
- [Axe CSV](#accessibility-violations-from-axe-csv)
- [Axe-core](#accessibility-violations-from-axe-core)
```

### Commented out code

The number of blocks of commented out lines of code.

Default target
: ≦ 0 blocks

Scales
: count

Default tags
: maintainability

```{admonition} Supporting sources
- [SonarQube](#commented-out-code-from-sonarqube)
```

### Complex units

The amount of units (classes, functions, methods, files) that are too complex.

Default target
: ≦ 0 complex units

Scales
: count (default)
: percentage

Default tags
: maintainability
: testability

```{admonition} Supporting sources
- [SonarQube](#complex-units-from-sonarqube)
```

### Dependencies

The amount of (outdated) dependencies.

Default target
: ≦ 0 dependencies

Scales
: count (default)
: percentage

Default tags
: maintainability

```{admonition} Supporting sources
- [Composer](#dependencies-from-composer)
- [npm](#dependencies-from-npm)
- [OWASP Dependency Check](#dependencies-from-owasp-dependency-check)
- [pip](#dependencies-from-pip)
```

### Duplicated lines

The amount of lines that are duplicated.

Default target
: ≦ 0 lines

Scales
: count (default)
: percentage

Default tags
: maintainability

```{admonition} Supporting sources
- [SonarQube](#duplicated-lines-from-sonarqube)
```

### Failed CI-jobs

The number of continuous integration jobs or pipelines that have failed.

Default target
: ≦ 0 CI-jobs

Scales
: count

Default tags
: ci

```{admonition} Supporting sources
- [Azure DevOps Server](#failed-ci-jobs-from-azure-devops-server)
- [Jenkins](#failed-ci-jobs-from-jenkins)
- [GitLab](#failed-ci-jobs-from-gitlab)
```

### Issues

The number of issues.

Default target
: ≦ 0 issues

Scales
: count

```{admonition} Supporting sources
- [Azure DevOps Server](#issues-from-azure-devops-server)
- [Jira](#issues-from-jira)
- [Trello](#issues-from-trello)
```

### Long units

The amount of units (functions, methods, files) that are too long.

Default target
: ≦ 0 long units

Scales
: count (default)
: percentage

Default tags
: maintainability

```{admonition} Supporting sources
- [SonarQube](#long-units-from-sonarqube)
```

### Manual test duration

The duration of the manual test in minutes.

Default target
: ≦ 0 minutes

Scales
: count

Default tags
: test quality

```{admonition} Supporting sources
- [Jira](#manual-test-duration-from-jira)
```

### Manual test execution

Measure the number of manual test cases that have not been tested on time.

Default target
: ≦ 0 manual test cases

Scales
: count

Default tags
: test quality

```{admonition} Supporting sources
- [Jira](#manual-test-execution-from-jira)
```

### Many parameters

The amount of units (functions, methods, procedures) that have too many parameters.

Default target
: ≦ 0 units with too many parameters

Scales
: count (default)
: percentage

Default tags
: maintainability

```{admonition} Supporting sources
- [SonarQube](#many-parameters-from-sonarqube)
```

### Merge requests

The amount of merge requests.

Default target
: ≦ 0 merge requests

Scales
: count (default)
: percentage

Default tags
: ci

```{admonition} Supporting sources
- [Azure DevOps Server](#merge-requests-from-azure-devops-server)
- [GitLab](#merge-requests-from-gitlab)
```

### Metrics

The amount of metrics from one more quality reports, with specific states and/or tags.

Default target
: ≦ 0 metrics

Scales
: count (default)
: percentage

```{admonition} Supporting sources
- [Quality-time](#metrics-from-quality-time)
```

### Missing metrics

Count the number of metrics that can be added to each report, but have not been added yet.

Default target
: ≦ 0 missing metrics

Scales
: count (default)
: percentage

```{admonition} Supporting sources
- [Quality-time](#missing-metrics-from-quality-time)
```

### Performancetest duration

The duration of the performancetest in minutes.

Default target
: ≧ 30 minutes

Scales
: count

Default tags
: performance

```{admonition} Supporting sources
- [Performancetest-runner](#performancetest-duration-from-performancetest-runner)
```

### Performancetest stability

The duration of the performancetest at which throughput or error count increases.

Default target
: ≧ 100% of the minutes

Scales
: percentage

Default tags
: performance

```{admonition} Supporting sources
- [Performancetest-runner](#performancetest-stability-from-performancetest-runner)
```

### Scalability

The percentage of (max) users at which ramp-up of throughput breaks.

Default target
: ≧ 75% of the users

Scales
: percentage

Default tags
: performance

```{admonition} Supporting sources
- [Performancetest-runner](#scalability-from-performancetest-runner)
```

### Security warnings

The number of security warnings about the software.

Default target
: ≦ 0 security warnings

Scales
: count

Default tags
: security

```{admonition} Supporting sources
- [Anchore](#security-warnings-from-anchore)
- [Anchore Jenkins plugin](#security-warnings-from-anchore-jenkins-plugin)
- [Bandit](#security-warnings-from-bandit)
- [Checkmarx CxSAST](#security-warnings-from-checkmarx-cxsast)
- [OpenVAS](#security-warnings-from-openvas)
- [OWASP Dependency Check](#security-warnings-from-owasp-dependency-check)
- [OWASP ZAP](#security-warnings-from-owasp-zap)
- [Pyupio Safety](#security-warnings-from-pyupio-safety)
- [Snyk](#security-warnings-from-snyk)
- [JSON file with security warnings](#security-warnings-from-json-file-with-security-warnings)
- [SonarQube](#security-warnings-from-sonarqube)
```

### Size (LOC)

The size of the software in lines of code.

Default target
: ≦ 30000 lines

Scales
: count

Default tags
: maintainability

```{admonition} Supporting sources
- [cloc](#size-loc-from-cloc)
- [SonarQube](#size-loc-from-sonarqube)
```

### Slow transactions

The number of transactions slower than their performance threshold.

Default target
: ≦ 0 transactions

Scales
: count

Default tags
: performance

```{admonition} Supporting sources
- [Performancetest-runner](#slow-transactions-from-performancetest-runner)
```

### Source up-to-dateness

The number of days since the source was last updated.

Default target
: ≦ 3 days

Scales
: count

Default tags
: ci

```{admonition} Supporting sources
- [Anchore](#source-up-to-dateness-from-anchore)
- [Anchore Jenkins plugin](#source-up-to-dateness-from-anchore-jenkins-plugin)
- [Axe-core](#source-up-to-dateness-from-axe-core)
- [Azure DevOps Server](#source-up-to-dateness-from-azure-devops-server)
- [Bandit](#source-up-to-dateness-from-bandit)
- [Calendar date](#source-up-to-dateness-from-calendar-date)
- [Cobertura](#source-up-to-dateness-from-cobertura)
- [Cobertura Jenkins plugin](#source-up-to-dateness-from-cobertura-jenkins-plugin)
- [Checkmarx CxSAST](#source-up-to-dateness-from-checkmarx-cxsast)
- [GitLab](#source-up-to-dateness-from-gitlab)
- [JaCoCo](#source-up-to-dateness-from-jacoco)
- [JaCoCo Jenkins plugin](#source-up-to-dateness-from-jacoco-jenkins-plugin)
- [Jenkins](#source-up-to-dateness-from-jenkins)
- [Jenkins test report](#source-up-to-dateness-from-jenkins-test-report)
- [JUnit XML report](#source-up-to-dateness-from-junit-xml-report)
- [NCover](#source-up-to-dateness-from-ncover)
- [Robot Framework](#source-up-to-dateness-from-robot-framework)
- [OpenVAS](#source-up-to-dateness-from-openvas)
- [OWASP Dependency Check](#source-up-to-dateness-from-owasp-dependency-check)
- [OWASP ZAP](#source-up-to-dateness-from-owasp-zap)
- [Performancetest-runner](#source-up-to-dateness-from-performancetest-runner)
- [Quality-time](#source-up-to-dateness-from-quality-time)
- [Robot Framework Jenkins plugin](#source-up-to-dateness-from-robot-framework-jenkins-plugin)
- [SonarQube](#source-up-to-dateness-from-sonarqube)
- [TestNG](#source-up-to-dateness-from-testng)
- [Trello](#source-up-to-dateness-from-trello)
```

### Source version

The version number of the source.

Default target
: ≧ 1.0

Scales
: version_number

Default tags
: ci

```{admonition} Supporting sources
- [Axe-core](#source-version-from-axe-core)
- [cloc](#source-version-from-cloc)
- [Cobertura](#source-version-from-cobertura)
- [Checkmarx CxSAST](#source-version-from-checkmarx-cxsast)
- [GitLab](#source-version-from-gitlab)
- [Jenkins](#source-version-from-jenkins)
- [Jira](#source-version-from-jira)
- [OpenVAS](#source-version-from-openvas)
- [OWASP Dependency Check](#source-version-from-owasp-dependency-check)
- [OWASP ZAP](#source-version-from-owasp-zap)
- [Quality-time](#source-version-from-quality-time)
- [Robot Framework](#source-version-from-robot-framework)
- [SonarQube](#source-version-from-sonarqube)
```

### Suppressed violations

The amount of violations suppressed in the source.

Default target
: ≦ 0 suppressed violations

Scales
: count (default)
: percentage

Default tags
: maintainability

```{admonition} Supporting sources
- [SonarQube](#suppressed-violations-from-sonarqube)
```

### Test branch coverage

The amount of code branches not covered by tests.

Default target
: ≦ 0 uncovered branches

Scales
: count (default)
: percentage

Default tags
: test quality

```{admonition} Supporting sources
- [Cobertura](#test-branch-coverage-from-cobertura)
- [Cobertura Jenkins plugin](#test-branch-coverage-from-cobertura-jenkins-plugin)
- [JaCoCo](#test-branch-coverage-from-jacoco)
- [JaCoCo Jenkins plugin](#test-branch-coverage-from-jacoco-jenkins-plugin)
- [NCover](#test-branch-coverage-from-ncover)
- [SonarQube](#test-branch-coverage-from-sonarqube)
```

### Test cases

The amount of test cases.

Default target
: ≧ 0 test cases

Scales
: count (default)
: percentage

Default tags
: test quality

```{admonition} Supporting sources
- [Jira](#test-cases-from-jira)
- [JUnit XML report](#test-cases-from-junit-xml-report)
- [TestNG](#test-cases-from-testng)
```

### Test line coverage

The amount of lines of code not covered by tests.

Default target
: ≦ 0 uncovered lines

Scales
: count (default)
: percentage

Default tags
: test quality

```{admonition} Supporting sources
- [Cobertura](#test-line-coverage-from-cobertura)
- [Cobertura Jenkins plugin](#test-line-coverage-from-cobertura-jenkins-plugin)
- [JaCoCo](#test-line-coverage-from-jacoco)
- [JaCoCo Jenkins plugin](#test-line-coverage-from-jacoco-jenkins-plugin)
- [NCover](#test-line-coverage-from-ncover)
- [SonarQube](#test-line-coverage-from-sonarqube)
```

### Tests

The amount of tests.

Default target
: ≧ 0 tests

Scales
: count (default)
: percentage

Default tags
: test quality

```{admonition} Supporting sources
- [Azure DevOps Server](#tests-from-azure-devops-server)
- [Jenkins test report](#tests-from-jenkins-test-report)
- [JUnit XML report](#tests-from-junit-xml-report)
- [Performancetest-runner](#tests-from-performancetest-runner)
- [Robot Framework](#tests-from-robot-framework)
- [Robot Framework Jenkins plugin](#tests-from-robot-framework-jenkins-plugin)
- [SonarQube](#tests-from-sonarqube)
- [TestNG](#tests-from-testng)
```

### Unmerged branches

The number of branches that have not been merged to the default branch.

Default target
: ≦ 0 branches

Scales
: count

Default tags
: ci

```{admonition} Supporting sources
- [Azure DevOps Server](#unmerged-branches-from-azure-devops-server)
- [GitLab](#unmerged-branches-from-gitlab)
```

### Unused CI-jobs

The number of continuous integration jobs that are unused.

Default target
: ≦ 0 CI-jobs

Scales
: count

Default tags
: ci

```{admonition} Supporting sources
- [Azure DevOps Server](#unused-ci-jobs-from-azure-devops-server)
- [GitLab](#unused-ci-jobs-from-gitlab)
- [Jenkins](#unused-ci-jobs-from-jenkins)
```

### User story points

The total number of points of a selection of user stories.

Default target
: ≧ 100 user story points

Scales
: count

Default tags
: process efficiency

```{admonition} Supporting sources
- [Azure DevOps Server](#user-story-points-from-azure-devops-server)
- [Jira](#user-story-points-from-jira)
```

### Velocity

The average number of user story points delivered in recent sprints.

Default target
: ≧ 20 user story points per sprint

Scales
: count

Default tags
: process efficiency

```{admonition} Supporting sources
- [Jira](#velocity-from-jira)
```

### Violation remediation effort

The amount of effort it takes to remediate violations.

Default target
: ≦ 60 minutes

Scales
: count

Default tags
: maintainability

```{admonition} Supporting sources
- [SonarQube](#violation-remediation-effort-from-sonarqube)
```

### Violations

The number of violations of programming rules in the software.

Default target
: ≦ 0 violations

Scales
: count

Default tags
: maintainability

```{admonition} Supporting sources
- [OJAudit](#violations-from-ojaudit)
- [SonarQube](#violations-from-sonarqube)
```

## Sources

This is an overview of all the sources that *Quality-time* can use to measure metrics. For each source, the metrics that the source can measure are listed. Also, a link to the source's own documentation is provided.

### Anchore

Anchore image scan analysis report in JSON format.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-anchore)
- [Security warnings](#security-warnings-from-anchore)
```

```{seealso}
[https://docs.anchore.com/current/docs/using/integration/ci_cd/inline_scanning/](https://docs.anchore.com/current/docs/using/integration/ci_cd/inline_scanning/)
```

### Anchore Jenkins plugin

A Jenkins job with an Anchore report produced by the Anchore Jenkins plugin.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-anchore-jenkins-plugin)
- [Security warnings](#security-warnings-from-anchore-jenkins-plugin)
```

```{seealso}
[https://plugins.jenkins.io/anchore-container-scanner/](https://plugins.jenkins.io/anchore-container-scanner/)
```

### Axe CSV

An Axe accessibility report in CSV format.

```{admonition} Supported metrics
- [Accessibility violations](#accessibility-violations-from-axe-csv)
```

```{seealso}
[https://github.com/ICTU/axe-reports](https://github.com/ICTU/axe-reports)
```

### Axe-core

Axe is an accessibility testing engine for websites and other HTML-based user interfaces.

```{admonition} Supported metrics
- [Accessibility violations](#accessibility-violations-from-axe-core)
- [Source up-to-dateness](#source-up-to-dateness-from-axe-core)
- [Source version](#source-version-from-axe-core)
```

```{seealso}
[https://github.com/dequelabs/axe-core](https://github.com/dequelabs/axe-core)
```

### Azure DevOps Server

Azure DevOps Server (formerly known as Team Foundation Server) by Microsoft provides source code management, reporting, requirements management, project management, automated builds, testing and release management.

```{admonition} Supported metrics
- [Failed CI-jobs](#failed-ci-jobs-from-azure-devops-server)
- [Issues](#issues-from-azure-devops-server)
- [Merge requests](#merge-requests-from-azure-devops-server)
- [Source up-to-dateness](#source-up-to-dateness-from-azure-devops-server)
- [Tests](#tests-from-azure-devops-server)
- [Unmerged branches](#unmerged-branches-from-azure-devops-server)
- [Unused CI-jobs](#unused-ci-jobs-from-azure-devops-server)
- [User story points](#user-story-points-from-azure-devops-server)
```

```{seealso}
[https://azure.microsoft.com/en-us/services/devops/server/](https://azure.microsoft.com/en-us/services/devops/server/)
```

### Bandit

Bandit is a tool designed to find common security issues in Python code.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-bandit)
- [Security warnings](#security-warnings-from-bandit)
```

```{seealso}
[https://github.com/PyCQA/bandit](https://github.com/PyCQA/bandit)
```

### Calendar date

Warn when the date is too long ago. Can be used to, for example, warn when it is time for the next security test.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-calendar-date)
```

### Checkmarx CxSAST

Static analysis software to identify security vulnerabilities in both custom code and open source components.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-checkmarx-cxsast)
- [Source version](#source-version-from-checkmarx-cxsast)
- [Security warnings](#security-warnings-from-checkmarx-cxsast)
```

```{seealso}
[https://checkmarx.com/glossary/static-application-security-testing-sast/](https://checkmarx.com/glossary/static-application-security-testing-sast/)
```

### Cobertura

Cobertura is a free Java tool that calculates the percentage of code accessed by tests.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-cobertura)
- [Source version](#source-version-from-cobertura)
- [Test branch coverage](#test-branch-coverage-from-cobertura)
- [Test line coverage](#test-line-coverage-from-cobertura)
```

```{seealso}
[https://cobertura.github.io/cobertura/](https://cobertura.github.io/cobertura/)
```

### Cobertura Jenkins plugin

Jenkins plugin for Cobertura, a free Java tool that calculates the percentage of code accessed by tests.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-cobertura-jenkins-plugin)
- [Test branch coverage](#test-branch-coverage-from-cobertura-jenkins-plugin)
- [Test line coverage](#test-line-coverage-from-cobertura-jenkins-plugin)
```

```{seealso}
[https://plugins.jenkins.io/cobertura/](https://plugins.jenkins.io/cobertura/)
```

### Composer

A Dependency Manager for PHP.

```{admonition} Supported metrics
- [Dependencies](#dependencies-from-composer)
```

```{seealso}
[https://getcomposer.org/](https://getcomposer.org/)
```

### GitLab

GitLab provides Git-repositories, wiki's, issue-tracking and continuous integration/continuous deployment pipelines.

```{admonition} Supported metrics
- [Failed CI-jobs](#failed-ci-jobs-from-gitlab)
- [Merge requests](#merge-requests-from-gitlab)
- [Source up-to-dateness](#source-up-to-dateness-from-gitlab)
- [Source version](#source-version-from-gitlab)
- [Unmerged branches](#unmerged-branches-from-gitlab)
- [Unused CI-jobs](#unused-ci-jobs-from-gitlab)
```

```{seealso}
[https://about.gitlab.com/](https://about.gitlab.com/)
```

### JSON file with security warnings

A generic vulnerability report with security warnings in JSON format.

```{admonition} Supported metrics
- [Security warnings](#security-warnings-from-json-file-with-security-warnings)
```

```{seealso}
[https://quality-time.readthedocs.io/en/latest/usage.html#generic-json-for-security-warnings](https://quality-time.readthedocs.io/en/latest/usage.html#generic-json-for-security-warnings)
```

### JUnit XML report

Test reports in the JUnit XML format.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-junit-xml-report)
- [Test cases](#test-cases-from-junit-xml-report)
- [Tests](#tests-from-junit-xml-report)
```

```{seealso}
[https://junit.org/junit5/](https://junit.org/junit5/)
```

### JaCoCo

JaCoCo is an open-source tool for measuring and reporting Java code coverage.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-jacoco)
- [Test branch coverage](#test-branch-coverage-from-jacoco)
- [Test line coverage](#test-line-coverage-from-jacoco)
```

```{seealso}
[https://www.eclemma.org/jacoco/](https://www.eclemma.org/jacoco/)
```

### JaCoCo Jenkins plugin

A Jenkins job with a JaCoCo coverage report produced by the JaCoCo Jenkins plugin.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-jacoco-jenkins-plugin)
- [Test branch coverage](#test-branch-coverage-from-jacoco-jenkins-plugin)
- [Test line coverage](#test-line-coverage-from-jacoco-jenkins-plugin)
```

```{seealso}
[https://plugins.jenkins.io/jacoco](https://plugins.jenkins.io/jacoco)
```

### Jenkins

Jenkins is an open source continuous integration/continuous deployment server.

```{admonition} Supported metrics
- [Failed CI-jobs](#failed-ci-jobs-from-jenkins)
- [Source up-to-dateness](#source-up-to-dateness-from-jenkins)
- [Source version](#source-version-from-jenkins)
- [Unused CI-jobs](#unused-ci-jobs-from-jenkins)
```

```{seealso}
[https://www.jenkins.io/](https://www.jenkins.io/)
```

### Jenkins test report

A Jenkins job with test results.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-jenkins-test-report)
- [Tests](#tests-from-jenkins-test-report)
```

```{seealso}
[https://plugins.jenkins.io/junit](https://plugins.jenkins.io/junit)
```

### Jira

Jira is a proprietary issue tracker developed by Atlassian supporting bug tracking and agile project management.

```{admonition} Supported metrics
- [Issues](#issues-from-jira)
- [Manual test duration](#manual-test-duration-from-jira)
- [Manual test execution](#manual-test-execution-from-jira)
- [Source version](#source-version-from-jira)
- [Test cases](#test-cases-from-jira)
- [User story points](#user-story-points-from-jira)
- [Velocity](#velocity-from-jira)
```

```{seealso}
[https://www.atlassian.com/software/jira](https://www.atlassian.com/software/jira)
```

### Manual number

A manual number.

```{admonition} Supported metrics
All metrics with the count or percentage scale can be measured with this source).
```

### NCover

A .NET code coverage solution.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-ncover)
- [Test branch coverage](#test-branch-coverage-from-ncover)
- [Test line coverage](#test-line-coverage-from-ncover)
```

```{seealso}
[https://www.ncover.com/](https://www.ncover.com/)
```

### OJAudit

An Oracle JDeveloper program to audit Java code against JDeveloper's audit rules.

```{admonition} Supported metrics
- [Violations](#violations-from-ojaudit)
```

```{seealso}
[https://www.oracle.com/application-development/technologies/jdeveloper.html](https://www.oracle.com/application-development/technologies/jdeveloper.html)
```

### OWASP Dependency Check

Dependency-Check is a utility that identifies project dependencies and checks if there are any known, publicly disclosed, vulnerabilities.

```{admonition} Supported metrics
- [Dependencies](#dependencies-from-owasp-dependency-check)
- [Source up-to-dateness](#source-up-to-dateness-from-owasp-dependency-check)
- [Source version](#source-version-from-owasp-dependency-check)
- [Security warnings](#security-warnings-from-owasp-dependency-check)
```

```{seealso}
[https://owasp.org/www-project-dependency-check/](https://owasp.org/www-project-dependency-check/)
```

### OWASP ZAP

The OWASP Zed Attack Proxy (ZAP) can help automatically find security vulnerabilities in web applications while the application is being developed and tested.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-owasp-zap)
- [Source version](#source-version-from-owasp-zap)
- [Security warnings](#security-warnings-from-owasp-zap)
```

```{seealso}
[https://owasp.org/www-project-zap/](https://owasp.org/www-project-zap/)
```

### OpenVAS

OpenVAS (Open Vulnerability Assessment System) is a software framework of several services and tools offering vulnerability scanning and vulnerability management.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-openvas)
- [Source version](#source-version-from-openvas)
- [Security warnings](#security-warnings-from-openvas)
```

```{seealso}
[https://www.openvas.org](https://www.openvas.org)
```

### Performancetest-runner

An open source tool to run performancetests and create performancetest reports.

```{admonition} Supported metrics
- [Performancetest duration](#performancetest-duration-from-performancetest-runner)
- [Performancetest stability](#performancetest-stability-from-performancetest-runner)
- [Scalability](#scalability-from-performancetest-runner)
- [Slow transactions](#slow-transactions-from-performancetest-runner)
- [Source up-to-dateness](#source-up-to-dateness-from-performancetest-runner)
- [Tests](#tests-from-performancetest-runner)
```

```{seealso}
[https://github.com/ICTU/performancetest-runner](https://github.com/ICTU/performancetest-runner)
```

### Pyupio Safety

Safety checks Python dependencies for known security vulnerabilities.

```{admonition} Supported metrics
- [Security warnings](#security-warnings-from-pyupio-safety)
```

```{seealso}
[https://github.com/pyupio/safety](https://github.com/pyupio/safety)
```

### Quality-time

Quality report software for software development and maintenance.

```{admonition} Supported metrics
- [Metrics](#metrics-from-quality-time)
- [Missing metrics](#missing-metrics-from-quality-time)
- [Source up-to-dateness](#source-up-to-dateness-from-quality-time)
- [Source version](#source-version-from-quality-time)
```

```{seealso}
[https://github.com/ICTU/quality-time](https://github.com/ICTU/quality-time)
```

### Robot Framework

Robot Framework is a generic open source automation framework for acceptance testing, acceptance test driven development, and robotic process automation.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-robot-framework)
- [Source version](#source-version-from-robot-framework)
- [Tests](#tests-from-robot-framework)
```

```{seealso}
[https://robotframework.org](https://robotframework.org)
```

### Robot Framework Jenkins plugin

A Jenkins plugin for Robot Framework, a generic open source automation framework for acceptance testing, acceptance test driven development, and robotic process automation.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-robot-framework-jenkins-plugin)
- [Tests](#tests-from-robot-framework-jenkins-plugin)
```

```{seealso}
[https://plugins.jenkins.io/robot/](https://plugins.jenkins.io/robot/)
```

### Snyk

Snyk vulnerability report in JSON format.

```{admonition} Supported metrics
- [Security warnings](#security-warnings-from-snyk)
```

```{seealso}
[https://support.snyk.io/hc/en-us/articles/360003812458-Getting-started-with-the-CLI](https://support.snyk.io/hc/en-us/articles/360003812458-Getting-started-with-the-CLI)
```

### SonarQube

SonarQube is an open-source platform for continuous inspection of code quality to perform automatic reviews with static analysis of code to detect bugs, code smells, and security vulnerabilities on 20+ programming languages.

```{admonition} Supported metrics
- [Commented out code](#commented-out-code-from-sonarqube)
- [Complex units](#complex-units-from-sonarqube)
- [Duplicated lines](#duplicated-lines-from-sonarqube)
- [Size (LOC)](#size-loc-from-sonarqube)
- [Long units](#long-units-from-sonarqube)
- [Many parameters](#many-parameters-from-sonarqube)
- [Violation remediation effort](#violation-remediation-effort-from-sonarqube)
- [Source up-to-dateness](#source-up-to-dateness-from-sonarqube)
- [Source version](#source-version-from-sonarqube)
- [Security warnings](#security-warnings-from-sonarqube)
- [Suppressed violations](#suppressed-violations-from-sonarqube)
- [Tests](#tests-from-sonarqube)
- [Test branch coverage](#test-branch-coverage-from-sonarqube)
- [Test line coverage](#test-line-coverage-from-sonarqube)
- [Violations](#violations-from-sonarqube)
```

```{seealso}
[https://www.sonarqube.org](https://www.sonarqube.org)
```

### TestNG

Test reports in the TestNG XML format.

```{admonition} Supported metrics
- [Source up-to-dateness](#source-up-to-dateness-from-testng)
- [Test cases](#test-cases-from-testng)
- [Tests](#tests-from-testng)
```

```{seealso}
[https://testng.org](https://testng.org)
```

### Trello

Trello is a collaboration tool that organizes projects into boards.

```{admonition} Supported metrics
- [Issues](#issues-from-trello)
- [Source up-to-dateness](#source-up-to-dateness-from-trello)
```

```{seealso}
[https://trello.com](https://trello.com)
```

### cloc

cloc is an open-source tool for counting blank lines, comment lines, and physical lines of source code in many programming languages.

```{admonition} Supported metrics
- [Size (LOC)](#size-loc-from-cloc)
- [Source version](#source-version-from-cloc)
```

```{seealso}
[https://github.com/AlDanial/cloc](https://github.com/AlDanial/cloc)
```

### npm

npm is a package manager for the JavaScript programming language.

```{admonition} Supported metrics
- [Dependencies](#dependencies-from-npm)
```

```{seealso}
[https://docs.npmjs.com/](https://docs.npmjs.com/)
```

### pip

pip is the package installer for Python. You can use pip to install packages from the Python Package Index and other indexes.

```{admonition} Supported metrics
- [Dependencies](#dependencies-from-pip)
```

```{seealso}
[https://pip.pypa.io/en/stable/](https://pip.pypa.io/en/stable/)
```

## Metric-source combinations

This is an overview of all supported combinations of metrics and sources. For each combination of metric and source, the mandatory and optional parameters are listed that can be used to configure the source to measure the metric. If *Quality-time* needs to make certain assumptions about the source, for example which SonarQube rules to use to count long methods, then these assumptions are listed under 'configurations'.

### Accessibility violations from Axe CSV

[Axe CSV](#axe-csv) can be used to measure [accessibility violations](#accessibility-violations).

Mandatory parameters:

- **URL to an Axe report in CSV format or to a zip with Axe reports in CSV format**.

Optional parameters:

- **Impact levels**. If provided, only count accessibility violations with the selected impact levels. This parameter is multiple choice. Possible impact levels are: `critical`, `minor`, `moderate`, `serious`. The default value is: _all impact levels_.
- **Password for basic authentication**.
- **Private token**.
- **URL to an Axe report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Axe report in CSV format.
- **Username for basic authentication**.
- **Violation types**. This parameter is multiple choice. Possible violation types are: `accesskeys`, `area-alt`, `aria-allowed-attr`, `aria-allowed-role`, `aria-dpub-role-fallback`, `aria-hidden-body`, `aria-hidden-focus`, `aria-input-field-name`, `aria-required-attr`, `aria-required-children`, `aria-required-parent`, `aria-roledescription`, `aria-roles`, `aria-toggle-field-name`, `aria-valid-attr-value`, `aria-valid-attr`, `audio-caption`, `autocomplete-valid`, `avoid-inline-spacing`, `blink`, `button-name`, `bypass`, `checkboxgroup`, `color-contrast`, `css-orientation-lock`, `definition-list`, `dlitem`, `document-title`, `duplicate-id-active`, `duplicate-id-aria`, `duplicate-id`, `empty-heading`, `focus-order-semantics`, `form-field-multiple-labels`, `frame-tested`, `frame-title-unique`, `frame-title`, `heading-order`, `hidden-content`, `html-has-lang`, `html-lang-valid`, `html-xml-lang-mismatch`, `image-alt`, `image-redundant-alt`, `input-button-name`, `input-image-alt`, `label-content-name-mismatch`, `label-title-only`, `label`, `landmark-banner-is-top-level`, `landmark-complementary-is-top-level`, `landmark-contentinfo-is-top-level`, `landmark-main-is-top-level`, `landmark-no-duplicate-banner`, `landmark-no-duplicate-contentinfo`, `landmark-one-main`, `landmark-unique`, `layout-table`, `link-in-text-block`, `link-name`, `list`, `listitem`, `marquee`, `meta-refresh`, `meta-viewport-large`, `meta-viewport`, `object-alt`, `p-as-heading`, `page-has-heading-one`, `radiogroup`, `region`, `role-img-alt`, `scope-attr-valid`, `scrollable-region-focusable`, `server-side-image-map`, `skip-link`, `tabindex`, `table-duplicate-name`, `table-fake-caption`, `td-has-header`, `td-headers-attr`, `th-has-data-cells`, `valid-lang`, `video-caption`, `video-description`. The default value is: _all violation types_.

  ```{seealso}
  [https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
  ```

### Accessibility violations from Axe-core

[Axe-core](#axe-core) can be used to measure [accessibility violations](#accessibility-violations).

Mandatory parameters:

- **URL to an Axe-core report in JSON format or to a zip with Axe-core reports in JSON format**.

Optional parameters:

- **Impact levels**. If provided, only count accessibility violations with the selected impact levels. This parameter is multiple choice. Possible impact levels are: `critical`, `minor`, `moderate`, `serious`. The default value is: _all impact levels_.
- **Password for basic authentication**.
- **Private token**.
- **Result types**. Limit which result types to count. This parameter is multiple choice. Possible result types are: `inapplicable`, `incomplete`, `passes`, `violations`. The default value is: `violations`.
- **Tags to ignore (regular expressions or tags)**. Tags to ignore can be specified by tag or by regular expression.
- **Tags to include (regular expressions or tags)**. Tags to include can be specified by tag or by regular expression.
- **URL to an Axe-core report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Axe-core report in JSON format.
- **Username for basic authentication**.

### Commented out code from SonarQube

[SonarQube](#sonarqube) can be used to measure [commented out code](#commented-out-code).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

Configurations:

- Rules used to detect commented out code:
  - abap:S125
  - apex:S125
  - c:CommentedCode
  - cpp:CommentedCode
  - csharpsquid:S125
  - flex:CommentedCode
  - java:S125
  - javascript:CommentedCode
  - javascript:S125
  - kotlin:S125
  - objc:CommentedCode
  - php:S125
  - plsql:S125
  - python:S125
  - scala:S125
  - squid:CommentedOutCodeLine
  - swift:S125
  - typescript:S125
  - Web:AvoidCommentedOutCodeCheck
  - xml:S125

### Complex units from SonarQube

[SonarQube](#sonarqube) can be used to measure [complex units](#complex-units).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

Configurations:

- Rules used to detect complex units:
  - csharpsquid:S1541
  - csharpsquid:S3776
  - flex:FunctionComplexity
  - go:S3776
  - java:S1541
  - javascript:FunctionComplexity
  - javascript:S1541
  - javascript:S3776
  - kotlin:S3776
  - php:S1541
  - php:S3776
  - python:FunctionComplexity
  - python:S3776
  - ruby:S3776
  - scala:S3776
  - squid:MethodCyclomaticComplexity
  - squid:S3776
  - typescript:S1541
  - typescript:S3776
  - vbnet:S1541
  - vbnet:S3776

### Dependencies from Composer

[Composer](#composer) can be used to measure [dependencies](#dependencies).

Mandatory parameters:

- **URL to a Composer 'outdated' report in JSON format or to a zip with Composer 'outdated' reports in JSON format**.

  ```{seealso}
  [https://getcomposer.org/doc/03-cli.md#outdated](https://getcomposer.org/doc/03-cli.md#outdated)
  ```

Optional parameters:

- **Latest version statuses**. Limit which latest version statuses to show. The status 'safe update possible' means that based on semantic versioning the update should be backwards compatible. This parameter is multiple choice. Possible statuses are: `safe update possible`, `unknown`, `up-to-date`, `update possible`. The default value is: _all statuses_.
- **Password for basic authentication**.
- **Private token**.
- **URL to a Composer 'outdated' report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Composer 'outdated' report in JSON format.
- **Username for basic authentication**.

### Dependencies from npm

[npm](#npm) can be used to measure [dependencies](#dependencies).

Mandatory parameters:

- **URL to a npm 'outdated' report in JSON format or to a zip with npm 'outdated' reports in JSON format**.

  ```{seealso}
  [https://docs.npmjs.com/cli-commands/outdated.html](https://docs.npmjs.com/cli-commands/outdated.html)
  ```

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a npm 'outdated' report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the npm 'outdated' report in JSON format.
- **Username for basic authentication**.

### Dependencies from OWASP Dependency Check

[OWASP Dependency Check](#owasp-dependency-check) can be used to measure [dependencies](#dependencies).

Mandatory parameters:

- **URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an OWASP Dependency Check report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OWASP Dependency Check report in XML format.
- **Username for basic authentication**.

### Dependencies from pip

[pip](#pip) can be used to measure [dependencies](#dependencies).

Mandatory parameters:

- **URL to a pip 'outdated' report in JSON format or to a zip with pip 'outdated' reports in JSON format**.

  ```{seealso}
  [https://pip.pypa.io/en/stable/reference/pip_list/](https://pip.pypa.io/en/stable/reference/pip_list/)
  ```

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a pip 'outdated' report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the pip 'outdated' report in JSON format.
- **Username for basic authentication**.

### Duplicated lines from SonarQube

[SonarQube](#sonarqube) can be used to measure [duplicated lines](#duplicated-lines).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

### Failed CI-jobs from Azure DevOps Server

[Azure DevOps Server](#azure-devops-server) can be used to measure [failed ci-jobs](#failed-ci-jobs).

Mandatory parameters:

- **URL including organization and project**. URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'.

Optional parameters:

- **Failure types**. Limit which failure types to count as failed. This parameter is multiple choice. Possible failure types are: `canceled`, `failed`, `no result`, `partially succeeded`. The default value is: _all failure types_.
- **Pipelines to ignore (regular expressions or pipeline names)**. Pipelines to ignore can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders.
- **Pipelines to include (regular expressions or pipeline names)**. Pipelines to include can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders.
- **Private token**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
  ```

### Failed CI-jobs from Jenkins

[Jenkins](#jenkins) can be used to measure [failed ci-jobs](#failed-ci-jobs).

Mandatory parameters:

- **URL**. URL of the Jenkins instance, with port if necessary, but without path. For example, 'https://jenkins.example.org'.

Optional parameters:

- **Failure types**. Limit which failure types to count as failed. This parameter is multiple choice. Possible failure types are: `Aborted`, `Failure`, `Not built`, `Unstable`. The default value is: _all failure types_.
- **Jobs to ignore (regular expressions or job names)**. Jobs to ignore can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs.
- **Jobs to include (regular expressions or job names)**. Jobs to include can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs.
- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Failed CI-jobs from GitLab

[GitLab](#gitlab) can be used to measure [failed ci-jobs](#failed-ci-jobs).

Mandatory parameters:

- **GitLab instance URL**. URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'.
- **Project (name with namespace or id)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/)
  ```

Optional parameters:

- **Branches and tags to ignore (regular expressions, branch names or tag names)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/)
  ```

- **Failure types**. Limit which failure types to count as failed. This parameter is multiple choice. Possible failure types are: `canceled`, `failed`, `skipped`. The default value is: _all failure types_.
- **Jobs to ignore (regular expressions or job names)**. Jobs to ignore can be specified by job name or by regular expression.
- **Private token (with read_api scope)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
  ```

### Issues from Azure DevOps Server

[Azure DevOps Server](#azure-devops-server) can be used to measure [issues](#issues).

Mandatory parameters:

- **Issue query in WIQL (Work Item Query Language)**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops)
  ```

- **URL including organization and project**. URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'.

Optional parameters:

- **Private token**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
  ```

### Issues from Jira

[Jira](#jira) can be used to measure [issues](#issues).

Mandatory parameters:

- **Issue query in JQL (Jira Query Language)**.

  ```{seealso}
  [https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
  ```

- **URL**. URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'.

Optional parameters:

- **Password for basic authentication**.
- **Username for basic authentication**.

### Issues from Trello

[Trello](#trello) can be used to measure [issues](#issues).

Mandatory parameters:

- **Board (title or id)**.

  ```{seealso}
  [https://trello.com/1/members/me/boards?fields=name](https://trello.com/1/members/me/boards?fields=name)
  ```

- **URL**. The default value is: `https://trello.com`.

Optional parameters:

- **API key**.

  ```{seealso}
  [https://trello.com/app-key](https://trello.com/app-key)
  ```

- **Cards to count**. This parameter is multiple choice. Possible cards are: `inactive`, `overdue`. The default value is: _all cards_.
- **Lists to ignore (title or id)**.
- **Number of days without activity after which to consider cards inactive**. The default value is: `30`.
- **Token**.

  ```{seealso}
  [https://trello.com/app-key](https://trello.com/app-key)
  ```

### Size (LOC) from cloc

[cloc](#cloc) can be used to measure [size (loc)](#size-loc).

Mandatory parameters:

- **URL to a cloc report in JSON format or to a zip with cloc reports in JSON format**.

Optional parameters:

- **Languages to ignore (regular expressions or language names)**.

  ```{seealso}
  [https://github.com/AlDanial/cloc#recognized-languages-](https://github.com/AlDanial/cloc#recognized-languages-)
  ```

- **Password for basic authentication**.
- **Private token**.
- **URL to a cloc report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the cloc report in JSON format.
- **Username for basic authentication**.

### Size (LOC) from SonarQube

[SonarQube](#sonarqube) can be used to measure [size (loc)](#size-loc).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Languages to ignore (regular expressions or language names)**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/analysis/languages/overview/](https://docs.sonarqube.org/latest/analysis/languages/overview/)
  ```

- **Lines to count**. Either count all lines including lines with comments or only count lines with code, excluding comments. Note: it's possible to ignore specific languages only when counting lines with code. This is a SonarQube limitation. This parameter is single choice. Possible lines to count are: `all lines`, `lines with code`. The default value is: `lines with code`.
- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

### Long units from SonarQube

[SonarQube](#sonarqube) can be used to measure [long units](#long-units).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

Configurations:

- Rules used to detect long units:
  - abap:S104
  - c:FileLoc
  - cpp:FileLoc
  - csharpsquid:S104
  - csharpsquid:S138
  - flex:S138
  - go:S104
  - go:S138
  - java:S138
  - javascript:S104
  - javascript:S138
  - kotlin:S104
  - kotlin:S138
  - objc:FileLoc
  - php:S104
  - php:S138
  - php:S2042
  - Pylint:R0915
  - python:S104
  - ruby:S104
  - ruby:S138
  - scala:S104
  - scala:S138
  - squid:S00104
  - squid:S1188
  - squid:S138
  - squid:S2972
  - swift:S104
  - typescript:S104
  - typescript:S138
  - vbnet:S104
  - vbnet:S138
  - Web:FileLengthCheck
  - Web:LongJavaScriptCheck

### Manual test duration from Jira

[Jira](#jira) can be used to measure [manual test duration](#manual-test-duration).

Mandatory parameters:

- **Issue query in JQL (Jira Query Language)**.

  ```{seealso}
  [https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
  ```

- **Manual test duration field (name or id)**.

  ```{seealso}
  [https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html)
  ```

- **URL**. URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'.

Optional parameters:

- **Password for basic authentication**.
- **Username for basic authentication**.

### Manual test execution from Jira

[Jira](#jira) can be used to measure [manual test execution](#manual-test-execution).

Mandatory parameters:

- **Default expected manual test execution frequency (days)**. Specify how often the manual tests should be executed. For example, if the sprint length is three weeks, manual tests should be executed at least once every 21 days. The default value is: `21`.
- **Issue query in JQL (Jira Query Language)**.

  ```{seealso}
  [https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
  ```

- **URL**. URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'.

Optional parameters:

- **Manual test execution frequency field (name or id)**.

  ```{seealso}
  [https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html)
  ```

- **Password for basic authentication**.
- **Username for basic authentication**.

### Many parameters from SonarQube

[SonarQube](#sonarqube) can be used to measure [many parameters](#many-parameters).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

Configurations:

- Rules used to detect units with many parameters:
  - c:S107
  - cpp:S107
  - csharpsquid:S107
  - csharpsquid:S2436
  - flex:S107
  - java:S107
  - javascript:ExcessiveParameterList
  - javascript:S107
  - objc:S107
  - php:S107
  - plsql:PlSql.FunctionAndProcedureExcessiveParameters
  - python:S107
  - squid:S00107
  - tsql:S107
  - typescript:S107

### Merge requests from Azure DevOps Server

[Azure DevOps Server](#azure-devops-server) can be used to measure [merge requests](#merge-requests).

Mandatory parameters:

- **URL including organization and project**. URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'.

Optional parameters:

- **Merge request states**. Limit which merge request states to count. This parameter is multiple choice. Possible states are: `abandoned`, `active`, `completed`, `not set`. The default value is: _all states_.
- **Minimum number of upvotes**. Only count merge requests with fewer than the minimum number of upvotes. The default value is: `0`.
- **Private token**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
  ```

- **Repository (name or id)**.
- **Target branches to include (regular expressions or branch names)**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops)
  ```

### Merge requests from GitLab

[GitLab](#gitlab) can be used to measure [merge requests](#merge-requests).

Mandatory parameters:

- **GitLab instance URL**. URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'.
- **Project (name with namespace or id)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/)
  ```

Optional parameters:

- **Approval states to include (requires GitLab Premium)**. This parameter is multiple choice. Possible approval states are: `approved`, `not approved`, `unknown`. The default value is: _all approval states_.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/merge_requests/approvals/](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
  ```

- **Merge request states**. Limit which merge request states to count. This parameter is multiple choice. Possible states are: `closed`, `locked`, `merged`, `opened`. The default value is: _all states_.
- **Minimum number of upvotes**. Only count merge requests with fewer than the minimum number of upvotes. The default value is: `0`.
- **Private token (with read_api scope)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
  ```

- **Target branches to include (regular expressions or branch names)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/)
  ```

### Metrics from Quality-time

[Quality-time](#quality-time) can be used to measure [metrics](#metrics).

Mandatory parameters:

- **Quality-time URL**. URL of the Quality-time instance, with port if necessary, but without path. For example, 'https://quality-time.example.org'.

Optional parameters:

- **Metric statuses**. This parameter is multiple choice. Possible metric statuses are: `near target met (yellow)`, `target met (green)`, `target not met (red)`, `technical debt target met (grey)`, `unknown (white)`. The default value is: _all metric statuses_.
- **Metric types**. If provided, only count metrics with the selected metric types. This parameter is multiple choice. Possible metric types are: `Accessibility violations`, `Commented out code`, `Complex units`, `Dependencies`, `Duplicated lines`, `Failed CI-jobs`, `Issues`, `Long units`, `Manual test duration`, `Manual test execution`, `Many parameters`, `Merge requests`, `Metrics`, `Missing metrics`, `Performancetest duration`, `Performancetest stability`, `Ready user story points`, `Scalability`, `Security warnings`, `Size (LOC)`, `Slow transactions`, `Source up-to-dateness`, `Source version`, `Suppressed violations`, `Test branch coverage`, `Test cases`, `Test line coverage`, `Tests`, `Unmerged branches`, `Unused CI-jobs`, `User story points`, `Velocity`, `Violation remediation effort`, `Violations`. The default value is: _all metric types_.
- **Report names or identifiers**.
- **Source types**. If provided, only count metrics with one or more sources of the selected source types. This parameter is multiple choice. Possible source types are: `Anchore Jenkins plugin`, `Anchore`, `Axe CSV`, `Axe-core`, `Azure DevOps Server`, `Bandit`, `Calendar date`, `Checkmarx CxSAST`, `Cobertura Jenkins plugin`, `Cobertura`, `Composer`, `GitLab`, `JSON file with security warnings`, `JUnit XML report`, `JaCoCo Jenkins plugin`, `JaCoCo`, `Jenkins test report`, `Jenkins`, `Jira`, `Manual number`, `NCover`, `OJAudit`, `OWASP Dependency Check`, `OWASP ZAP`, `OpenVAS`, `Performancetest-runner`, `Pyupio Safety`, `Quality-time`, `Robot Framework Jenkins plugin`, `Robot Framework`, `Snyk`, `SonarQube`, `TestNG`, `Trello`, `cloc`, `npm`, `pip`. The default value is: _all source types_.
- **Tags**. If provided, only count metrics with one ore more of the given tags.

### Missing metrics from Quality-time

[Quality-time](#quality-time) can be used to measure [missing metrics](#missing-metrics).

Mandatory parameters:

- **Quality-time URL**. URL of the Quality-time instance, with port if necessary, but without path. For example, 'https://quality-time.example.org'.

Optional parameters:

- **Report names or identifiers**.

### Performancetest duration from Performancetest-runner

[Performancetest-runner](#performancetest-runner) can be used to measure [performancetest duration](#performancetest-duration).

Mandatory parameters:

- **URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Username for basic authentication**.

### Performancetest stability from Performancetest-runner

[Performancetest-runner](#performancetest-runner) can be used to measure [performancetest stability](#performancetest-stability).

Mandatory parameters:

- **URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Username for basic authentication**.

### Violation remediation effort from SonarQube

[SonarQube](#sonarqube) can be used to measure [violation remediation effort](#violation-remediation-effort).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

- **Types of effort**. This parameter is multiple choice. Possible effort types are: `effort to fix all bug issues`, `effort to fix all code smells`, `effort to fix all vulnerabilities`. The default value is: _all effort types_.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/metric-definitions/](https://docs.sonarqube.org/latest/user-guide/metric-definitions/)
  ```

### Scalability from Performancetest-runner

[Performancetest-runner](#performancetest-runner) can be used to measure [scalability](#scalability).

Mandatory parameters:

- **URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Username for basic authentication**.

### Slow transactions from Performancetest-runner

[Performancetest-runner](#performancetest-runner) can be used to measure [slow transactions](#slow-transactions).

Mandatory parameters:

- **URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Thresholds**. If provided, only count transactions that surpass the selected thresholds. This parameter is multiple choice. Possible thresholds are: `high`, `warning`. The default value is: _all thresholds_.
- **Transactions to ignore (regular expressions or transaction names)**. Transactions to ignore can be specified by transaction name or by regular expression.
- **Transactions to include (regular expressions or transaction names)**. Transactions to include can be specified by transaction name or by regular expression.
- **Username for basic authentication**.

### Source up-to-dateness from Anchore

[Anchore](#anchore) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to an Anchore details report in JSON format or to a zip with Anchore details reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an Anchore vulnerability report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Anchore vulnerability report in JSON format.
- **Username for basic authentication**.

### Source up-to-dateness from Anchore Jenkins plugin

[Anchore Jenkins plugin](#anchore-jenkins-plugin) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with an Anchore report generated by the Anchore plugin. For example, 'https://jenkins.example.org/job/anchore' or https://jenkins.example.org/job/anchore/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Source up-to-dateness from Axe-core

[Axe-core](#axe-core) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to an Axe-core report in JSON format or to a zip with Axe-core reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an Axe-core report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Axe-core report in JSON format.
- **Username for basic authentication**.

### Source up-to-dateness from Azure DevOps Server

[Azure DevOps Server](#azure-devops-server) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL including organization and project**. URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'.

Optional parameters:

- **Branch**. The default value is: `master`.
- **File or folder path**. Use the date and time the path was last changed to determine the up-to-dateness. Note that if a pipeline is specified, the pipeline is used to determine the up-to-dateness, and the path is ignored.
- **Pipelines to ignore (regular expressions or pipeline names)**. Pipelines to ignore can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders.
- **Pipelines to include (regular expressions or pipeline names)**. Pipelines to include can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders.
- **Private token**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
  ```

- **Repository (name or id)**.

### Source up-to-dateness from Bandit

[Bandit](#bandit) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to a Bandit report in JSON format or to a zip with Bandit reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a Bandit report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Bandit report in JSON format.
- **Username for basic authentication**.

### Source up-to-dateness from Calendar date

[Calendar date](#calendar-date) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **Date**. The default value is: `2021-01-01`.

### Source up-to-dateness from Cobertura

[Cobertura](#cobertura) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to a Cobertura report in XML format or to a zip with Cobertura reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a Cobertura report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Cobertura report in XML format.
- **Username for basic authentication**.

### Source up-to-dateness from Cobertura Jenkins plugin

[Cobertura Jenkins plugin](#cobertura-jenkins-plugin) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a coverage report generated by the Cobertura plugin. For example, 'https://jenkins.example.org/job/cobertura' or https://jenkins.example.org/job/cobertura/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Source up-to-dateness from Checkmarx CxSAST

[Checkmarx CxSAST](#checkmarx-cxsast) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **Password for basic authentication**.
- **Project (name or id)**.
- **URL**. URL of the Checkmarx instance, with port if necessary, but without path. For example 'https://checkmarx.example.org'.
- **Username for basic authentication**.

### Source up-to-dateness from GitLab

[GitLab](#gitlab) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **File or folder path**.

  ```{seealso}
  [https://docs.gitlab.com/ee/api/repository_files.html](https://docs.gitlab.com/ee/api/repository_files.html)
  ```

- **GitLab instance URL**. URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'.
- **Project (name with namespace or id)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/)
  ```

Optional parameters:

- **Branch**. The default value is: `master`.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/)
  ```

- **Private token (with read_api scope)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
  ```

### Source up-to-dateness from JaCoCo

[JaCoCo](#jacoco) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a JaCoCo report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the JaCoCo report in XML format.
- **Username for basic authentication**.

### Source up-to-dateness from JaCoCo Jenkins plugin

[JaCoCo Jenkins plugin](#jacoco-jenkins-plugin) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a coverage report generated by the JaCoCo plugin. For example, 'https://jenkins.example.org/job/jacoco' or https://jenkins.example.org/job/jacoco/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Source up-to-dateness from Jenkins

[Jenkins](#jenkins) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL**. URL of the Jenkins instance, with port if necessary, but without path. For example, 'https://jenkins.example.org'.

Optional parameters:

- **Build result types**. Limit which build result types to include. This parameter is multiple choice. Possible result types are: `Aborted`, `Failure`, `Not built`, `Success`, `Unstable`. The default value is: _all result types_.
- **Jobs to ignore (regular expressions or job names)**. Jobs to ignore can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs.
- **Jobs to include (regular expressions or job names)**. Jobs to include can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs.
- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Source up-to-dateness from Jenkins test report

[Jenkins test report](#jenkins-test-report) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a test report generated by the JUnit plugin. For example, 'https://jenkins.example.org/job/test' or https://jenkins.example.org/job/test/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Source up-to-dateness from JUnit XML report

[JUnit XML report](#junit-xml-report) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to a JUnit report in XML format or to a zip with JUnit reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a JUnit report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the JUnit report in XML format.
- **Username for basic authentication**.

### Source up-to-dateness from NCover

[NCover](#ncover) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to a NCover report in HTML format or to a zip with NCover reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Username for basic authentication**.

### Source up-to-dateness from Robot Framework

[Robot Framework](#robot-framework) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to a Robot Framework report in XML format or to a zip with Robot Framework reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a Robot Framework report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Robot Framework report in XML format.
- **Username for basic authentication**.

### Source up-to-dateness from OpenVAS

[OpenVAS](#openvas) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to an OpenVAS report in XML format or to a zip with OpenVAS reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an OpenVAS report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OpenVAS report in XML format.
- **Username for basic authentication**.

### Source up-to-dateness from OWASP Dependency Check

[OWASP Dependency Check](#owasp-dependency-check) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an OWASP Dependency Check report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OWASP Dependency Check report in XML format.
- **Username for basic authentication**.

### Source up-to-dateness from OWASP ZAP

[OWASP ZAP](#owasp-zap) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to an OWASP ZAP report in XML format or to a zip with OWASP ZAP reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an OWASP ZAP report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OWASP ZAP report in XML format.
- **Username for basic authentication**.

### Source up-to-dateness from Performancetest-runner

[Performancetest-runner](#performancetest-runner) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Username for basic authentication**.

### Source up-to-dateness from Quality-time

[Quality-time](#quality-time) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **Quality-time URL**. URL of the Quality-time instance, with port if necessary, but without path. For example, 'https://quality-time.example.org'.

Optional parameters:

- **Report names or identifiers**.

### Source up-to-dateness from Robot Framework Jenkins plugin

[Robot Framework Jenkins plugin](#robot-framework-jenkins-plugin) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a test report generated by the Robot Framework plugin. For example, 'https://jenkins.example.org/job/robot' or https://jenkins.example.org/job/robot/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Source up-to-dateness from SonarQube

[SonarQube](#sonarqube) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

### Source up-to-dateness from TestNG

[TestNG](#testng) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **URL to a TestNG report in XML format or to a zip with TestNG reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a TestNG report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the TestNG report in XML format.
- **Username for basic authentication**.

### Source up-to-dateness from Trello

[Trello](#trello) can be used to measure [source up-to-dateness](#source-up-to-dateness).

Mandatory parameters:

- **Board (title or id)**.

  ```{seealso}
  [https://trello.com/1/members/me/boards?fields=name](https://trello.com/1/members/me/boards?fields=name)
  ```

- **URL**. The default value is: `https://trello.com`.

Optional parameters:

- **API key**.

  ```{seealso}
  [https://trello.com/app-key](https://trello.com/app-key)
  ```

- **Lists to ignore (title or id)**.
- **Token**.

  ```{seealso}
  [https://trello.com/app-key](https://trello.com/app-key)
  ```

### Source version from Axe-core

[Axe-core](#axe-core) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL to an Axe-core report in JSON format or to a zip with Axe-core reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an Axe-core report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Axe-core report in JSON format.
- **Username for basic authentication**.

### Source version from cloc

[cloc](#cloc) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL to a cloc report in JSON format or to a zip with cloc reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a cloc report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the cloc report in JSON format.
- **Username for basic authentication**.

### Source version from Cobertura

[Cobertura](#cobertura) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL to a Cobertura report in XML format or to a zip with Cobertura reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a Cobertura report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Cobertura report in XML format.
- **Username for basic authentication**.

### Source version from Checkmarx CxSAST

[Checkmarx CxSAST](#checkmarx-cxsast) can be used to measure [source version](#source-version).

Mandatory parameters:

- **Password for basic authentication**.
- **URL**. URL of the Checkmarx instance, with port if necessary, but without path. For example 'https://checkmarx.example.org'.
- **Username for basic authentication**.

### Source version from GitLab

[GitLab](#gitlab) can be used to measure [source version](#source-version).

Mandatory parameters:

- **GitLab instance URL**. URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'.

Optional parameters:

- **Private token (with read_api scope)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
  ```

### Source version from Jenkins

[Jenkins](#jenkins) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL**. URL of the Jenkins instance, with port if necessary, but without path. For example, 'https://jenkins.example.org'.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Source version from Jira

[Jira](#jira) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL**. URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'.

Optional parameters:

- **Password for basic authentication**.
- **Username for basic authentication**.

### Source version from OpenVAS

[OpenVAS](#openvas) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL to an OpenVAS report in XML format or to a zip with OpenVAS reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an OpenVAS report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OpenVAS report in XML format.
- **Username for basic authentication**.

### Source version from OWASP Dependency Check

[OWASP Dependency Check](#owasp-dependency-check) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an OWASP Dependency Check report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OWASP Dependency Check report in XML format.
- **Username for basic authentication**.

### Source version from OWASP ZAP

[OWASP ZAP](#owasp-zap) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL to an OWASP ZAP report in XML format or to a zip with OWASP ZAP reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to an OWASP ZAP report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OWASP ZAP report in XML format.
- **Username for basic authentication**.

### Source version from Quality-time

[Quality-time](#quality-time) can be used to measure [source version](#source-version).

Mandatory parameters:

- **Quality-time URL**. URL of the Quality-time instance, with port if necessary, but without path. For example, 'https://quality-time.example.org'.

### Source version from Robot Framework

[Robot Framework](#robot-framework) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL to a Robot Framework report in XML format or to a zip with Robot Framework reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a Robot Framework report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Robot Framework report in XML format.
- **Username for basic authentication**.

### Source version from SonarQube

[SonarQube](#sonarqube) can be used to measure [source version](#source-version).

Mandatory parameters:

- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

### Security warnings from Anchore

[Anchore](#anchore) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to an Anchore vulnerability report in JSON format or to a zip with Anchore vulnerability reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Severities**. If provided, only count security warnings with the selected severities. This parameter is multiple choice. Possible severities are: `Critical`, `High`, `Low`, `Medium`, `Negligible`, `Unknown`. The default value is: _all severities_.
- **URL to an Anchore vulnerability report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Anchore vulnerability report in JSON format.
- **Username for basic authentication**.

### Security warnings from Anchore Jenkins plugin

[Anchore Jenkins plugin](#anchore-jenkins-plugin) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with an Anchore report generated by the Anchore plugin. For example, 'https://jenkins.example.org/job/anchore' or https://jenkins.example.org/job/anchore/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Severities**. If provided, only count security warnings with the selected severities. This parameter is multiple choice. Possible severities are: `Critical`, `High`, `Low`, `Medium`, `Negligible`, `Unknown`. The default value is: _all severities_.
- **Username for basic authentication**.

### Security warnings from Bandit

[Bandit](#bandit) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to a Bandit report in JSON format or to a zip with Bandit reports in JSON format**.

Optional parameters:

- **Confidence levels**. If provided, only count security warnings with the selected confidence levels. This parameter is multiple choice. Possible confidence levels are: `high`, `low`, `medium`. The default value is: _all confidence levels_.
- **Password for basic authentication**.
- **Private token**.
- **Severities**. If provided, only count security warnings with the selected severities. This parameter is multiple choice. Possible severities are: `high`, `low`, `medium`. The default value is: _all severities_.
- **URL to a Bandit report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Bandit report in JSON format.
- **Username for basic authentication**.

### Security warnings from Checkmarx CxSAST

[Checkmarx CxSAST](#checkmarx-cxsast) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **Password for basic authentication**.
- **Project (name or id)**.
- **URL**. URL of the Checkmarx instance, with port if necessary, but without path. For example 'https://checkmarx.example.org'.
- **Username for basic authentication**.

Optional parameters:

- **Severities**. If provided, only count security warnings with the selected severities. This parameter is multiple choice. Possible severities are: `high`, `info`, `low`, `medium`. The default value is: _all severities_.

### Security warnings from OpenVAS

[OpenVAS](#openvas) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to an OpenVAS report in XML format or to a zip with OpenVAS reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Severities**. If provided, only count security warnings with the selected severities. This parameter is multiple choice. Possible severities are: `high`, `log`, `low`, `medium`. The default value is: _all severities_.
- **URL to an OpenVAS report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OpenVAS report in XML format.
- **Username for basic authentication**.

### Security warnings from OWASP Dependency Check

[OWASP Dependency Check](#owasp-dependency-check) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Severities**. If provided, only count security warnings with the selected severities. This parameter is multiple choice. Possible severities are: `critical`, `high`, `low`, `medium`, `moderate`. The default value is: _all severities_.
- **URL to an OWASP Dependency Check report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OWASP Dependency Check report in XML format.
- **Username for basic authentication**.

### Security warnings from OWASP ZAP

[OWASP ZAP](#owasp-zap) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to an OWASP ZAP report in XML format or to a zip with OWASP ZAP reports in XML format**.

Optional parameters:

- **Count alert types or alert instances**. Determine whether to count each alert type in the OWASP ZAP report as a security warning or to count each alert instance (URL). This parameter is single choice. Possible count alert types or instances setting are: `alert instances`, `alert types`. The default value is: `alert instances`.
- **Parts of URLs to ignore (regular expressions)**. Parts of URLs to ignore can be specified by regular expression. The parts of URLs that match one or more of the regular expressions are removed. If, after applying the regular expressions, multiple warnings are the same only one is reported.
- **Password for basic authentication**.
- **Private token**.
- **Risks**. If provided, only count security warnings with the selected risks. This parameter is multiple choice. Possible risks are: `high`, `informational`, `low`, `medium`. The default value is: _all risks_.
- **URL to an OWASP ZAP report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OWASP ZAP report in XML format.
- **Username for basic authentication**.

### Security warnings from Pyupio Safety

[Pyupio Safety](#pyupio-safety) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to a Safety report in JSON format or to a zip with Safety reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a Safety report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Safety report in JSON format.
- **Username for basic authentication**.

### Security warnings from Snyk

[Snyk](#snyk) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to a Snyk vulnerability report in JSON format or to a zip with Snyk vulnerability reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Severities**. If provided, only count security warnings with the selected severities. This parameter is multiple choice. Possible severities are: `high`, `low`, `medium`. The default value is: _all severities_.
- **URL to a Snyk vulnerability report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Snyk vulnerability report in JSON format.
- **Username for basic authentication**.

### Security warnings from JSON file with security warnings

[JSON file with security warnings](#json-file-with-security-warnings) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **URL to a generic vulnerability report in JSON format or to a zip with generic vulnerability reports in JSON format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Severities**. If provided, only count security warnings with the selected severities. This parameter is multiple choice. Possible severities are: `high`, `low`, `medium`. The default value is: _all severities_.
- **URL to a generic vulnerability report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the generic vulnerability report in JSON format.
- **Username for basic authentication**.

### Security warnings from SonarQube

[SonarQube](#sonarqube) can be used to measure [security warnings](#security-warnings).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

- **Security hotspot review priorities**. This parameter is multiple choice. Possible review priorities are: `high`, `low`, `medium`. The default value is: _all review priorities_.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/security-hotspots/](https://docs.sonarqube.org/latest/user-guide/security-hotspots/)
  ```

- **Security issue types (measuring security hotspots requires SonarQube 8.2 or newer)**. This parameter is multiple choice. Possible types are: `security_hotspot`, `vulnerability`. The default value is: `vulnerability`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/rules/](https://docs.sonarqube.org/latest/user-guide/rules/)
  ```

- **Severities**. This parameter is multiple choice. Possible severities are: `blocker`, `critical`, `info`, `major`, `minor`. The default value is: _all severities_.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/issues/](https://docs.sonarqube.org/latest/user-guide/issues/)
  ```

### Suppressed violations from SonarQube

[SonarQube](#sonarqube) can be used to measure [suppressed violations](#suppressed-violations).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

- **Severities**. This parameter is multiple choice. Possible severities are: `blocker`, `critical`, `info`, `major`, `minor`. The default value is: _all severities_.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/issues/](https://docs.sonarqube.org/latest/user-guide/issues/)
  ```

- **Types**. This parameter is multiple choice. Possible types are: `bug`, `code_smell`, `vulnerability`. The default value is: _all types_.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/rules/](https://docs.sonarqube.org/latest/user-guide/rules/)
  ```

Configurations:

- Rules used to detect suppressed violations:
  - csharpsquid:S1309
  - java:NoSonar
  - java:S1309
  - java:S1310
  - java:S1315
  - php:NoSonar
  - Pylint:I0011
  - Pylint:I0020
  - squid:NoSonar
  - squid:S1309
  - squid:S1310
  - squid:S1315

### Test cases from Jira

[Jira](#jira) can be used to measure [test cases](#test-cases).

Mandatory parameters:

- **Issue query in JQL (Jira Query Language)**.

  ```{seealso}
  [https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
  ```

- **URL**. URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'.

Optional parameters:

- **Password for basic authentication**.
- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `errored`, `failed`, `passed`, `skipped`, `untested`. The default value is: _all test results_.
- **Username for basic authentication**.

### Test cases from JUnit XML report

[JUnit XML report](#junit-xml-report) can be used to measure [test cases](#test-cases).

Mandatory parameters:

- **URL to a JUnit report in XML format or to a zip with JUnit reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a JUnit report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the JUnit report in XML format.
- **Username for basic authentication**.

### Test cases from TestNG

[TestNG](#testng) can be used to measure [test cases](#test-cases).

Mandatory parameters:

- **URL to a TestNG report in XML format or to a zip with TestNG reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a TestNG report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the TestNG report in XML format.
- **Username for basic authentication**.

### Tests from Azure DevOps Server

[Azure DevOps Server](#azure-devops-server) can be used to measure [tests](#tests).

Mandatory parameters:

- **URL including organization and project**. URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'.

Optional parameters:

- **Names of test runs to include (regular expressions or test run names)**. Limit which test runs to include by test run name.
- **Private token**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
  ```

- **States of the test runs to include**. Limit which test runs to include by test run state. This parameter is multiple choice. Possible test run states are: `aborted`, `completed`, `in progress`, `not started`. The default value is: _all test run states_.
- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `failed`, `incomplete`, `not applicable`, `passed`. The default value is: _all test results_.

### Tests from Jenkins test report

[Jenkins test report](#jenkins-test-report) can be used to measure [tests](#tests).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a test report generated by the JUnit plugin. For example, 'https://jenkins.example.org/job/test' or https://jenkins.example.org/job/test/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `failed`, `passed`, `skipped`. The default value is: _all test results_.
- **Username for basic authentication**.

### Tests from JUnit XML report

[JUnit XML report](#junit-xml-report) can be used to measure [tests](#tests).

Mandatory parameters:

- **URL to a JUnit report in XML format or to a zip with JUnit reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `errored`, `failed`, `passed`, `skipped`. The default value is: _all test results_.
- **URL to a JUnit report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the JUnit report in XML format.
- **Username for basic authentication**.

### Tests from Performancetest-runner

[Performancetest-runner](#performancetest-runner) can be used to measure [tests](#tests).

Mandatory parameters:

- **URL to a Performancetest-runner report in HTML format or to a zip with Performancetest-runner reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `failed`, `success`. The default value is: _all test results_.
- **Transactions to ignore (regular expressions or transaction names)**. Transactions to ignore can be specified by transaction name or by regular expression.
- **Transactions to include (regular expressions or transaction names)**. Transactions to include can be specified by transaction name or by regular expression.
- **Username for basic authentication**.

### Tests from Robot Framework

[Robot Framework](#robot-framework) can be used to measure [tests](#tests).

Mandatory parameters:

- **URL to a Robot Framework report in XML format or to a zip with Robot Framework reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `fail`, `pass`, `skip`. The default value is: _all test results_.
- **URL to a Robot Framework report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Robot Framework report in XML format.
- **Username for basic authentication**.

### Tests from Robot Framework Jenkins plugin

[Robot Framework Jenkins plugin](#robot-framework-jenkins-plugin) can be used to measure [tests](#tests).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a test report generated by the Robot Framework plugin. For example, 'https://jenkins.example.org/job/robot' or https://jenkins.example.org/job/robot/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `fail`, `pass`. The default value is: _all test results_.
- **Username for basic authentication**.

### Tests from SonarQube

[SonarQube](#sonarqube) can be used to measure [tests](#tests).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `errored`, `failed`, `passed`, `skipped`. The default value is: _all test results_.

### Tests from TestNG

[TestNG](#testng) can be used to measure [tests](#tests).

Mandatory parameters:

- **URL to a TestNG report in XML format or to a zip with TestNG reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Test results**. Limit which test results to count. Note: depending on which results are selected, the direction of the metric may need to be adapted. For example, when counting passed tests, more is better, but when counting failed tests, fewer is better. This parameter is multiple choice. Possible test results are: `failed`, `ignored`, `passed`, `skipped`. The default value is: _all test results_.
- **URL to a TestNG report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the TestNG report in XML format.
- **Username for basic authentication**.

### Test branch coverage from Cobertura

[Cobertura](#cobertura) can be used to measure [test branch coverage](#test-branch-coverage).

Mandatory parameters:

- **URL to a Cobertura report in XML format or to a zip with Cobertura reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a Cobertura report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Cobertura report in XML format.
- **Username for basic authentication**.

### Test branch coverage from Cobertura Jenkins plugin

[Cobertura Jenkins plugin](#cobertura-jenkins-plugin) can be used to measure [test branch coverage](#test-branch-coverage).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a coverage report generated by the Cobertura plugin. For example, 'https://jenkins.example.org/job/cobertura' or https://jenkins.example.org/job/cobertura/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Test branch coverage from JaCoCo

[JaCoCo](#jacoco) can be used to measure [test branch coverage](#test-branch-coverage).

Mandatory parameters:

- **URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a JaCoCo report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the JaCoCo report in XML format.
- **Username for basic authentication**.

### Test branch coverage from JaCoCo Jenkins plugin

[JaCoCo Jenkins plugin](#jacoco-jenkins-plugin) can be used to measure [test branch coverage](#test-branch-coverage).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a coverage report generated by the JaCoCo plugin. For example, 'https://jenkins.example.org/job/jacoco' or https://jenkins.example.org/job/jacoco/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Test branch coverage from NCover

[NCover](#ncover) can be used to measure [test branch coverage](#test-branch-coverage).

Mandatory parameters:

- **URL to a NCover report in HTML format or to a zip with NCover reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Username for basic authentication**.

### Test branch coverage from SonarQube

[SonarQube](#sonarqube) can be used to measure [test branch coverage](#test-branch-coverage).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

### Test line coverage from Cobertura

[Cobertura](#cobertura) can be used to measure [test line coverage](#test-line-coverage).

Mandatory parameters:

- **URL to a Cobertura report in XML format or to a zip with Cobertura reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a Cobertura report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the Cobertura report in XML format.
- **Username for basic authentication**.

### Test line coverage from Cobertura Jenkins plugin

[Cobertura Jenkins plugin](#cobertura-jenkins-plugin) can be used to measure [test line coverage](#test-line-coverage).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a coverage report generated by the Cobertura plugin. For example, 'https://jenkins.example.org/job/cobertura' or https://jenkins.example.org/job/cobertura/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Test line coverage from JaCoCo

[JaCoCo](#jacoco) can be used to measure [test line coverage](#test-line-coverage).

Mandatory parameters:

- **URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **URL to a JaCoCo report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the JaCoCo report in XML format.
- **Username for basic authentication**.

### Test line coverage from JaCoCo Jenkins plugin

[JaCoCo Jenkins plugin](#jacoco-jenkins-plugin) can be used to measure [test line coverage](#test-line-coverage).

Mandatory parameters:

- **URL to Jenkins job**. URL to a Jenkins job with a coverage report generated by the JaCoCo plugin. For example, 'https://jenkins.example.org/job/jacoco' or https://jenkins.example.org/job/jacoco/job/master' in case of a pipeline job.

Optional parameters:

- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### Test line coverage from NCover

[NCover](#ncover) can be used to measure [test line coverage](#test-line-coverage).

Mandatory parameters:

- **URL to a NCover report in HTML format or to a zip with NCover reports in HTML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Username for basic authentication**.

### Test line coverage from SonarQube

[SonarQube](#sonarqube) can be used to measure [test line coverage](#test-line-coverage).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

### Unmerged branches from Azure DevOps Server

[Azure DevOps Server](#azure-devops-server) can be used to measure [unmerged branches](#unmerged-branches).

Mandatory parameters:

- **URL including organization and project**. URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'.

Optional parameters:

- **Branches to ignore (regular expressions or branch names)**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops)
  ```

- **Number of days since last commit after which to consider branches inactive**. The default value is: `7`.
- **Private token**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
  ```

- **Repository (name or id)**.

### Unmerged branches from GitLab

[GitLab](#gitlab) can be used to measure [unmerged branches](#unmerged-branches).

Mandatory parameters:

- **GitLab instance URL**. URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'.
- **Project (name with namespace or id)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/)
  ```

Optional parameters:

- **Branches to ignore (regular expressions or branch names)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/)
  ```

- **Number of days since last commit after which to consider branches inactive**. The default value is: `7`.
- **Private token (with read_api scope)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
  ```

### Unused CI-jobs from Azure DevOps Server

[Azure DevOps Server](#azure-devops-server) can be used to measure [unused ci-jobs](#unused-ci-jobs).

Mandatory parameters:

- **URL including organization and project**. URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'.

Optional parameters:

- **Number of days since last build after which to consider pipelines inactive**. The default value is: `21`.
- **Pipelines to ignore (regular expressions or pipeline names)**. Pipelines to ignore can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders.
- **Pipelines to include (regular expressions or pipeline names)**. Pipelines to include can be specified by pipeline name or by regular expression. Use {folder name}/{pipeline name} for the names of pipelines in folders.
- **Private token**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
  ```

### Unused CI-jobs from GitLab

[GitLab](#gitlab) can be used to measure [unused ci-jobs](#unused-ci-jobs).

Mandatory parameters:

- **GitLab instance URL**. URL of the GitLab instance, with port if necessary, but without path. For example, 'https://gitlab.com'.
- **Project (name with namespace or id)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/)
  ```

Optional parameters:

- **Branches and tags to ignore (regular expressions, branch names or tag names)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/project/repository/branches/](https://docs.gitlab.com/ee/user/project/repository/branches/)
  ```

- **Jobs to ignore (regular expressions or job names)**. Jobs to ignore can be specified by job name or by regular expression.
- **Number of days without builds after which to consider CI-jobs unused**. The default value is: `90`.
- **Private token (with read_api scope)**.

  ```{seealso}
  [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
  ```

### Unused CI-jobs from Jenkins

[Jenkins](#jenkins) can be used to measure [unused ci-jobs](#unused-ci-jobs).

Mandatory parameters:

- **URL**. URL of the Jenkins instance, with port if necessary, but without path. For example, 'https://jenkins.example.org'.

Optional parameters:

- **Jobs to ignore (regular expressions or job names)**. Jobs to ignore can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs.
- **Jobs to include (regular expressions or job names)**. Jobs to include can be specified by job name or by regular expression. Use {parent job name}/{child job name} for the names of nested jobs.
- **Number of days without builds after which to consider CI-jobs unused**. The default value is: `90`.
- **Password or API token for basic authentication**.

  ```{seealso}
  [https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/)
  ```

- **Username for basic authentication**.

### User story points from Azure DevOps Server

[Azure DevOps Server](#azure-devops-server) can be used to measure [user story points](#user-story-points).

Mandatory parameters:

- **Issue query in WIQL (Work Item Query Language)**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops)
  ```

- **URL including organization and project**. URL of the Azure DevOps instance, with port if necessary, and with organization and project. For example: 'https://dev.azure.com/{organization}/{project}'.

Optional parameters:

- **Private token**.

  ```{seealso}
  [https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
  ```

### User story points from Jira

[Jira](#jira) can be used to measure [user story points](#user-story-points).

Mandatory parameters:

- **Issue query in JQL (Jira Query Language)**.

  ```{seealso}
  [https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
  ```

- **Story points field (name or id)**. The default value is: `Story Points`.

  ```{seealso}
  [https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html)
  ```

- **URL**. URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'.

Optional parameters:

- **Password for basic authentication**.
- **Username for basic authentication**.

### Velocity from Jira

[Jira](#jira) can be used to measure [velocity](#velocity).

Mandatory parameters:

- **Board (name or id)**.

  ```{seealso}
  [https://support.atlassian.com/jira-software-cloud/docs/what-is-a-jira-software-board/](https://support.atlassian.com/jira-software-cloud/docs/what-is-a-jira-software-board/)
  ```

- **Number of sprints to base velocity on**. The default value is: `3`.
- **Type of velocity**. Whether to report the amount of story points committed to, the amount of story points actually completed, or the difference between the two. This parameter is single choice. Possible velocity type are: `committed points`, `completed points minus committed points`, `completed points`. The default value is: `completed points`.
- **URL**. URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'.

Optional parameters:

- **Password for basic authentication**.
- **Username for basic authentication**.

### Violations from OJAudit

[OJAudit](#ojaudit) can be used to measure [violations](#violations).

Mandatory parameters:

- **URL to an OJAudit report in XML format or to a zip with OJAudit reports in XML format**.

Optional parameters:

- **Password for basic authentication**.
- **Private token**.
- **Severities**. If provided, only count violations with the selected severities. This parameter is multiple choice. Possible severities are: `advisory`, `error`, `exception`, `incomplete`, `warning`. The default value is: _all severities_.
- **URL to an OJAudit report in a human readable format**. If provided, users clicking the source URL will visit this URL instead of the OJAudit report in XML format.
- **Username for basic authentication**.

### Violations from SonarQube

[SonarQube](#sonarqube) can be used to measure [violations](#violations).

Mandatory parameters:

- **Project key**. The project key can be found by opening the project in SonarQube and looking at the bottom of the grey column on the right.
- **URL**. URL of the SonarQube instance, with port if necessary, but without path. For example, 'https://sonarcloud.io'.

Optional parameters:

- **Branch (only supported by commercial SonarQube editions)**. The default value is: `master`.

  ```{seealso}
  [https://docs.sonarqube.org/latest/branches/overview/](https://docs.sonarqube.org/latest/branches/overview/)
  ```

- **Private token**.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/user-token/](https://docs.sonarqube.org/latest/user-guide/user-token/)
  ```

- **Severities**. This parameter is multiple choice. Possible severities are: `blocker`, `critical`, `info`, `major`, `minor`. The default value is: _all severities_.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/issues/](https://docs.sonarqube.org/latest/user-guide/issues/)
  ```

- **Types**. This parameter is multiple choice. Possible types are: `bug`, `code_smell`, `vulnerability`. The default value is: _all types_.

  ```{seealso}
  [https://docs.sonarqube.org/latest/user-guide/rules/](https://docs.sonarqube.org/latest/user-guide/rules/)
  ```
