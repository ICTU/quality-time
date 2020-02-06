# Quality-time data model

## Quality-time metrics

| Name | Description | Default target | Default tags | Sources¹ |
| ---- | ----------- | -------------- | ------------ | -------- |
| Accessibility violations | The number of accessibility violations in the web user interface of the software. | ≦ 0 violations | accessibility | Axe CSV |
| Commented out code | The number of lines of code commented out. | ≦ 0 lines | maintainability | SonarQube |
| Complex units | The amount of units (classes, functions, methods, files) that are too complex. | ≦ 0 complex units | maintainability, testability | SonarQube |
| Duplicated lines | The amount of lines that are duplicated. | ≦ 0 lines | maintainability | SonarQube |
| Failed CI-jobs | The number of continuous integration jobs or pipelines that have failed. | ≦ 0 CI-jobs | ci | Azure DevOps Server, Jenkins, GitLab |
| Issues | The number of issues. | ≦ 0 issues |  | Azure DevOps Server, Jira, Trello, Wekan |
| Size (LOC) | The size of the software in lines of code. | ≦ 30000 lines | maintainability | SonarQube |
| Long units | The amount of units (functions, methods, files) that are too long. | ≦ 0 long units | maintainability | SonarQube |
| Manual test duration | The duration of the manual test in minutes | ≦ 0 minutes | test quality | Jira |
| Manual test execution | Measure the number of manual test cases that have not been tested on time. | ≦ 0 manual test cases | test quality | Jira |
| Many parameters | The amount of units (functions, methods, procedures) that have too many parameters. | ≦ 0 units with too many parameters | maintainability | SonarQube |
| Metrics | The amount of metrics from one more quality reports, with specific states and/or tags. | ≦ 0 metrics |  | Quality-time |
| Performancetest duration | The duration of the performancetest in minutes | ≧ 30 minutes | performance | Performancetest-runner |
| Performancetest stability | The duration of the performancetest at which throughput or error count increases. | ≧ 100% of the minutes | performance | Performancetest-runner |
| Ready user story points | The number of points of user stories that are ready to implement. | ≧ 100 user story points | process efficiency | Azure DevOps Server, Jira |
| Scalability | The percentage of (max) users at which ramp-up of throughput breaks. | ≧ 75% of the users | performance | Performancetest-runner |
| Slow transactions | The number of transactions slower than their performance threshold. | ≦ 0 transactions | performance | Performancetest-runner |
| Source up-to-dateness | The number of days since the source was last updated. | ≦ 3 days | ci | Azure DevOps Server, Bandit, Calendar date, Checkmarx CxSAST, GitLab, JaCoCo, JaCoCo Jenkins plugin, Jenkins test report, JUnit XML report, NCover, Robot Framework, OpenVAS, OWASP Dependency Check, OWASP Dependency Check Jenkins plugin, OWASP ZAP, Performancetest-runner, SonarQube, Trello, Wekan |
| Security warnings | The number of security warnings about the software. | ≦ 0 security warnings | security | Bandit, Checkmarx CxSAST, OpenVAS, OWASP Dependency Check, OWASP Dependency Check Jenkins plugin, OWASP ZAP, Pyupio Safety |
| Suppressed violations | The amount of violations suppressed in the source. | ≦ 0 suppressed violations | maintainability | SonarQube |
| Tests | The number of tests. | ≧ 0 tests | test quality | Azure DevOps Server, Jenkins test report, JUnit XML report, Performancetest-runner, Robot Framework, SonarQube |
| Test branch coverage | The amount of code branches not covered by tests. | ≦ 0 uncovered branches | test quality | JaCoCo, JaCoCo Jenkins plugin, NCover, SonarQube |
| Test line coverage | The amount of lines of code not covered by tests. | ≦ 0 uncovered lines | test quality | JaCoCo, JaCoCo Jenkins plugin, NCover, SonarQube |
| Unmerged branches | The number of branches that have not been merged to master. | ≦ 0 branches | ci | Azure DevOps Server, GitLab |
| Unused CI-jobs | The number of continuous integration jobs that are unused. | ≦ 0 CI-jobs | ci | Azure DevOps Server, GitLab, Jenkins |
| Violations | The number of violations of programming rules in the software. | ≦ 0 violations | maintainability | OJAudit, SonarQube |

## Quality-time sources

| Name | Description | Metrics |
| ---- | ----------- | ------- |
| [Axe CSV](https://github.com/ICTU/axe-reports) | An Axe accessibility report in CSV format. | Accessibility violations |
| [Azure DevOps Server](https://azure.microsoft.com/en-us/services/devops/server/) | Azure DevOps Server (formerly known as Team Foundation Server) by Microsoft provides source code management, reporting, requirements management, project management, automated builds, testing and release management. | Failed CI-jobs, Issues, Ready user story points, Source up-to-dateness, Tests, Unmerged branches, Unused CI-jobs |
| [Bandit](https://github.com/PyCQA/bandit) | Bandit is a tool designed to find common security issues in Python code. | Source up-to-dateness, Security warnings |
| Calendar date | Warn when the date is too long ago. Can be used to e.g. warn when it's time for the next security test. | Source up-to-dateness |
| [Checkmarx CxSAST](https://www.checkmarx.com/products/static-application-security-testing/) | Static analysis software to identify security vulnerabilities in both custom code and open source components. | Source up-to-dateness, Security warnings |
| [GitLab](https://gitlab.com/) | GitLab provides Git-repositories, wiki's, issue-tracking and continuous integration/continuous deployment pipelines. | Failed CI-jobs, Source up-to-dateness, Unmerged branches, Unused CI-jobs |
| [JaCoCo](https://www.eclemma.org/jacoco/) | JaCoCo is an open-source tool for measuring and reporting Java code coverage. | Source up-to-dateness, Test branch coverage, Test line coverage |
| [Jenkins](https://jenkins.io/) | Jenkins is an open source continuous integration/continuous deployment server. | Failed CI-jobs, Unused CI-jobs |
| [JaCoCo Jenkins plugin](https://plugins.jenkins.io/jacoco) | A Jenkins job with a JaCoCo coverage report produced by the JaCoCo Jenkins plugin. | Source up-to-dateness, Test branch coverage, Test line coverage |
| [Jenkins test report](https://plugins.jenkins.io/junit) | A Jenkins job with test results. | Source up-to-dateness, Tests |
| [Jira](https://www.atlassian.com/software/jira) | Jira is a proprietary issue tracker developed by Atlassian supporting bug tracking and agile project management. | Issues, Manual test duration, Manual test execution, Ready user story points |
| [JUnit XML report](https://junit.org) | Test reports in the JUnit XML format. | Source up-to-dateness, Tests |
| Manual number | A manual number. | ¹ |
| [NCover](https://www.ncover.com/) | A .NET code coverage solution | Source up-to-dateness, Test branch coverage, Test line coverage |
| [OJAudit](https://www.oracle.com/technetwork/developer-tools/jdev) | An Oracle JDeveloper program to audit Java code against JDeveloper's audit rules. | Violations |
| [OpenVAS](http://www.openvas.org) | OpenVAS (Open Vulnerability Assessment System) is a software framework of several services and tools offering vulnerability scanning and vulnerability management. | Source up-to-dateness, Security warnings |
| [OWASP Dependency Check](https://www.owasp.org/index.php/OWASP_Dependency_Check) | Dependency-Check is a utility that identifies project dependencies and checks if there are any known, publicly disclosed, vulnerabilities. | Source up-to-dateness, Security warnings |
| [OWASP Dependency Check Jenkins plugin](https://plugins.jenkins.io/dependency-check-jenkins-plugin) | Jenkins plugin for the OWASP Dependency Check, a utility that identifies project dependencies and checks if there are any known, publicly disclosed, vulnerabilities. | Source up-to-dateness, Security warnings |
| [OWASP ZAP](https://www.owasp.org/index.php/OWASP_Zed_Attack_Proxy_Project) | The OWASP Zed Attack Proxy (ZAP) can help automatically find security vulnerabilities in web applications while the application is being developed and tested. | Source up-to-dateness, Security warnings |
| [Performancetest-runner](https://github.com/ICTU/performancetest-runner) | An open source tool to run performancetests and create performancetest reports. | Performancetest duration, Performancetest stability, Scalability, Slow transactions, Source up-to-dateness, Tests |
| [Pyupio Safety](https://github.com/pyupio/safety) | Safety checks Python dependencies for known security vulnerabilities. | Security warnings |
| [Quality-time](https://github.com/ICTU/quality-time) | Quality report software for software development and maintenance. | Metrics |
| [Random](https://en.wikipedia.org/wiki/Special:Random) | A source that generates random numbers, for testing purposes. | ¹ |
| [Robot Framework](https://robotframework.org) | Robot Framework is a generic open source automation framework for acceptance testing, acceptance test driven development, and robotic process automation. | Source up-to-dateness, Tests |
| [SonarQube](https://www.sonarqube.org) | SonarQube is an open-source platform for continuous inspection of code quality to perform automatic reviews with static analysis of code to detect bugs, code smells, and security vulnerabilities on 20+ programming languages. | Commented out code, Complex units, Duplicated lines, Size (LOC), Long units, Many parameters, Source up-to-dateness, Suppressed violations, Tests, Test branch coverage, Test line coverage, Violations |
| [Trello](https://trello.com) | Trello is a collaboration tool that organizes projects into boards. | Issues, Source up-to-dateness |
| [Wekan](https://wekan.github.io) | Open-source kanban. | Issues, Source up-to-dateness |

¹) All metrics can be measured using the 'Manual number' and the 'Random number' source.
