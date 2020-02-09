# Quality-time data model

## Quality-time metrics

| Name | Description | Default target | Default tags | Sources¹ |
| :--- | :---------- | :------------- | :----------- | :------- |
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
| Source up-to-dateness | The number of days since the source was last updated. | ≦ 3 days | ci | Anchore, Azure DevOps Server, Bandit, Calendar date, Checkmarx CxSAST, GitLab, JaCoCo, JaCoCo Jenkins plugin, Jenkins test report, JUnit XML report, NCover, Robot Framework, OpenVAS, OWASP Dependency Check, OWASP Dependency Check Jenkins plugin, OWASP ZAP, Performancetest-runner, SonarQube, Trello, Wekan |
| Security warnings | The number of security warnings about the software. | ≦ 0 security warnings | security | Anchore, Bandit, Checkmarx CxSAST, OpenVAS, OWASP Dependency Check, OWASP Dependency Check Jenkins plugin, OWASP ZAP, Pyupio Safety |
| Suppressed violations | The amount of violations suppressed in the source. | ≦ 0 suppressed violations | maintainability | SonarQube |
| Tests | The number of tests. | ≧ 0 tests | test quality | Azure DevOps Server, Jenkins test report, JUnit XML report, Performancetest-runner, Robot Framework, SonarQube |
| Test branch coverage | The amount of code branches not covered by tests. | ≦ 0 uncovered branches | test quality | JaCoCo, JaCoCo Jenkins plugin, NCover, SonarQube |
| Test line coverage | The amount of lines of code not covered by tests. | ≦ 0 uncovered lines | test quality | JaCoCo, JaCoCo Jenkins plugin, NCover, SonarQube |
| Unmerged branches | The number of branches that have not been merged to master. | ≦ 0 branches | ci | Azure DevOps Server, GitLab |
| Unused CI-jobs | The number of continuous integration jobs that are unused. | ≦ 0 CI-jobs | ci | Azure DevOps Server, GitLab, Jenkins |
| Violations | The number of violations of programming rules in the software. | ≦ 0 violations | maintainability | OJAudit, SonarQube |

## Quality-time sources

| Name | Description | Metrics |
| :--- | :---------- | :------ |
| [Anchore](https://docs.anchore.com/current/docs/using/integration/ci_cd/inline_scanning/) | Anchore image scan analysis report in JSON format | Source up-to-dateness, Security warnings |
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
## Supported metric/source combinations

### Accessibility violations from Axe CSV

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an Axe report in CSV format or to a zip with Axe reports in CSV format | URL | Yes |
| URL to Axe report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Impact levels | Multiple choice | No |
| [Violation types](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md) | Multiple choice | No |

### Commented out code from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |
| [Rules](https://rules.sonarsource.com) | Multiple choice with addition | No |

### Complex units from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |
| [Rules](https://rules.sonarsource.com) | Multiple choice with addition | No |

### Duplicated lines from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |

### Failed CI-jobs from Azure DevOps Server

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL including organization and project (e.g. https://dev.azure.com/{organization}/{project} | URL | Yes |
| [Private token](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) | Password | No |
| Pipelines to ignore (regular expressions or pipeline names, use <folder>/<pipeline name> for pipelines in folders) | Multiple choice with addition | No |
| Failure type | Multiple choice | No |

### Failed CI-jobs from Jenkins

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Jobs to ignore (regular expressions or job names, use <parent job name>/<child job name> for the names of nested jobs) | Multiple choice with addition | No |
| Failure type | Multiple choice | No |

### Failed CI-jobs from GitLab

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| GitLab instance URL | URL | Yes |
| [Project (name with namespace or id)](https://docs.gitlab.com/ee/user/project/) | String | Yes |
| [Private token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) | Password | No |
| Failure type | Multiple choice | No |

### Issues from Azure DevOps Server

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL including organization and project (e.g. https://dev.azure.com/{organization}/{project} | URL | Yes |
| [Private token](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) | Password | No |
| [Issue query in WIQL (Work Item Query Language)](https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops) | String | Yes |

### Issues from Jira

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Issue query in JQL (Jira Query Language)](https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html) | String | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Issues from Trello

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [API key](https://trello.com/app-key) | String | No |
| [Token](https://trello.com/app-key) | String | No |
| [Board (title or id)](https://trello.com/1/members/me/boards?fields=name) | String | Yes |
| Lists to ignore (title or id) | Multiple choice with addition | No |
| Cards to count | Multiple choice | No |
| Number of days without activity after which to consider cards inactive | Integer | No |

### Issues from Wekan

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| Board (title or id) | String | No |
| Username | String | No |
| Password | Password | No |
| Lists to ignore (title or id) | Multiple choice with addition | No |
| Cards to count | Multiple choice | No |
| Number of days without activity after which to consider cards inactive | Integer | No |

### Size (LOC) from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |
| Lines to count | Single choice | No |

### Long units from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |
| [Rules](https://rules.sonarsource.com) | Multiple choice with addition | No |

### Manual test duration from Jira

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Issue query in JQL (Jira Query Language)](https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html) | String | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| [Manual test duration field (name or id)](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html) | String | Yes |

### Manual test execution from Jira

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Issue query in JQL (Jira Query Language)](https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html) | String | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| [Manual test execution frequency field (name or id)](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html) | String | No |
| Default expected manual test execution frequency (days) | Integer | Yes |

### Many parameters from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |
| [Rules](https://rules.sonarsource.com) | Multiple choice with addition | No |

### Metrics from Quality-time

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| Quality-time URL | URL | Yes |
| Metric status | Multiple choice | No |
| Report names or identifiers | Multiple choice with addition | No |
| Metric types | Multiple choice | No |
| Source types | Multiple choice | No |
| Tags | Multiple choice with addition | No |

### Performancetest duration from Performancetest-runner

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Performancetest-runner HTML report or a zip with Performancetest-runner HTML reports | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Performancetest stability from Performancetest-runner

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Performancetest-runner HTML report or a zip with Performancetest-runner HTML reports | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Ready user story points from Azure DevOps Server

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL including organization and project (e.g. https://dev.azure.com/{organization}/{project} | URL | Yes |
| [Private token](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) | Password | No |
| [Issue query in WIQL (Work Item Query Language)](https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops) | String | Yes |

### Ready user story points from Jira

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Issue query in JQL (Jira Query Language)](https://confluence.atlassian.com/jirasoftwarecloud/advanced-searching-764478330.html) | String | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| [Story points field (name or id)](https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html) | String | Yes |

### Scalability from Performancetest-runner

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Performancetest-runner HTML report or a zip with Performancetest-runner HTML reports | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Slow transactions from Performancetest-runner

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Performancetest-runner HTML report or a zip with Performancetest-runner HTML reports | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Thresholds | Multiple choice | No |

### Source up-to-dateness from Anchore

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an Anchore details report in JSON format or to a zip with Anchore reports in JSON format | URL | Yes |
| URL to Anchore report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from Azure DevOps Server

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL including organization and project (e.g. https://dev.azure.com/{organization}/{project} | URL | Yes |
| [Private token](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) | Password | No |
| File or folder path | String | Yes |
| Repository (name or id) | String | No |
| Branch | String | No |

### Source up-to-dateness from Bandit

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Bandit JSON-report or to a zip with Bandit JSON-reports | URL | Yes |
| URL to Bandit report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from Calendar date

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| Date | Date | Yes |

### Source up-to-dateness from Checkmarx CxSAST

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| Project (name or id) | String | Yes |
| Username for basic authentication | String | Yes |
| Password for basic authentication | Password | Yes |

### Source up-to-dateness from GitLab

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| GitLab instance URL | URL | Yes |
| [Project (name with namespace or id)](https://docs.gitlab.com/ee/user/project/) | String | Yes |
| [Private token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) | Password | No |
| [File or folder path](https://docs.gitlab.com/ee/api/repository_files.html) | String | Yes |
| [Branch](https://docs.gitlab.com/ee/user/project/repository/branches/) | String | No |

### Source up-to-dateness from JaCoCo

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format | URL | Yes |
| URL to a JaCoCo report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from JaCoCo Jenkins plugin

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to job | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from Jenkins test report

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to job | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from JUnit XML report

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a JUnit report in XML format or to a zip with JUnit reports in XML format | URL | Yes |
| URL to a JUnit report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from NCover

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a NCover report in HTML format or to a zip with NCover reports in HTML format | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from Robot Framework

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Robot Framework report in XML format or a zip with Robot Framework reports in XML format | URL | Yes |
| URL to a Robot Framework report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from OpenVAS

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an OpenVAS report in XML format or to a zip with OpenVAS reports in XML format | URL | Yes |
| URL to an OpenVAS report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from OWASP Dependency Check

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format | URL | Yes |
| URL to OWASP Dependency Check report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from OWASP Dependency Check Jenkins plugin

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to Jenkins job | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from OWASP ZAP

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an OWASP ZAP report in XML format or to a zip with OWASP ZAP reports in XML format | URL | Yes |
| URL to an OWASP ZAP report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from Performancetest-runner

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Performancetest-runner HTML report or a zip with Performancetest-runner HTML reports | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Source up-to-dateness from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |

### Source up-to-dateness from Trello

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [API key](https://trello.com/app-key) | String | No |
| [Token](https://trello.com/app-key) | String | No |
| [Board (title or id)](https://trello.com/1/members/me/boards?fields=name) | String | Yes |
| Lists to ignore (title or id) | Multiple choice with addition | No |

### Source up-to-dateness from Wekan

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| Board (title or id) | String | No |
| Username | String | No |
| Password | Password | No |
| Lists to ignore (title or id) | Multiple choice with addition | No |

### Security warnings from Anchore

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an Anchore vulnerability report in JSON format or to a zip with Anchore reports in JSON format | URL | Yes |
| URL to Anchore report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Severities | Multiple choice | No |

### Security warnings from Bandit

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Bandit JSON-report or to a zip with Bandit JSON-reports | URL | Yes |
| URL to Bandit report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Severities | Multiple choice | No |
| Confidence levels | Multiple choice | No |

### Security warnings from Checkmarx CxSAST

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| Project (name or id) | String | Yes |
| Username for basic authentication | String | Yes |
| Password for basic authentication | Password | Yes |
| Severities | Multiple choice | No |

### Security warnings from OpenVAS

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an OpenVAS report in XML format or to a zip with OpenVAS reports in XML format | URL | Yes |
| URL to an OpenVAS report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Severities | Multiple choice | No |

### Security warnings from OWASP Dependency Check

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an OWASP Dependency Check report in XML format or to a zip with OWASP Dependency Check reports in XML format | URL | Yes |
| URL to OWASP Dependency Check report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Severities | Multiple choice | No |

### Security warnings from OWASP Dependency Check Jenkins plugin

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to Jenkins job | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Severities | Multiple choice | No |

### Security warnings from OWASP ZAP

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an OWASP ZAP report in XML format or to a zip with OWASP ZAP reports in XML format | URL | Yes |
| URL to an OWASP ZAP report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Risks | Multiple choice | No |

### Security warnings from Pyupio Safety

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Safety report in JSON format or a zip with Safety reports in JSON format. | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Suppressed violations from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |
| [Severities](https://docs.sonarqube.org/latest/user-guide/issues/) | Multiple choice | No |
| [Rules](https://rules.sonarsource.com) | Multiple choice with addition | No |
| [Types](https://docs.sonarqube.org/latest/user-guide/rules/) | Multiple choice | No |

### Tests from Azure DevOps Server

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL including organization and project (e.g. https://dev.azure.com/{organization}/{project} | URL | Yes |
| [Private token](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) | Password | No |
| Test result | Multiple choice | No |

### Tests from Jenkins test report

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to job | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Test result | Multiple choice | No |

### Tests from JUnit XML report

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a JUnit report in XML format or to a zip with JUnit reports in XML format | URL | Yes |
| URL to a JUnit report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Test result | Multiple choice | No |

### Tests from Performancetest-runner

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Performancetest-runner HTML report or a zip with Performancetest-runner HTML reports | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Test result | Multiple choice | No |

### Tests from Robot Framework

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a Robot Framework report in XML format or a zip with Robot Framework reports in XML format | URL | Yes |
| URL to a Robot Framework report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Test result | Multiple choice | No |

### Tests from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |
| Test result | Multiple choice | No |

### Test branch coverage from JaCoCo

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format | URL | Yes |
| URL to a JaCoCo report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Test branch coverage from JaCoCo Jenkins plugin

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to job | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Test branch coverage from NCover

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a NCover report in HTML format or to a zip with NCover reports in HTML format | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Test branch coverage from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |

### Test line coverage from JaCoCo

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a JaCoCo report in XML format or to a zip with JaCoCo reports in XML format | URL | Yes |
| URL to a JaCoCo report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Test line coverage from JaCoCo Jenkins plugin

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to job | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Test line coverage from NCover

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to a NCover report in HTML format or to a zip with NCover reports in HTML format | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |

### Test line coverage from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |

### Unmerged branches from Azure DevOps Server

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL including organization and project (e.g. https://dev.azure.com/{organization}/{project} | URL | Yes |
| [Private token](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) | Password | No |
| Repository (name or id) | String | No |
| [Branches to ignore (regular expressions or branch names)](https://docs.gitlab.com/ee/user/project/repository/branches/) | Multiple choice with addition | No |
| Number of days since last commit after which to consider branches inactive | Integer | No |

### Unmerged branches from GitLab

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| GitLab instance URL | URL | Yes |
| [Project (name with namespace or id)](https://docs.gitlab.com/ee/user/project/) | String | Yes |
| [Private token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) | Password | No |
| [Branches to ignore (regular expressions or branch names)](https://docs.gitlab.com/ee/user/project/repository/branches/) | Multiple choice with addition | No |
| Number of days since last commit after which to consider branches inactive | Integer | No |

### Unused CI-jobs from Azure DevOps Server

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL including organization and project (e.g. https://dev.azure.com/{organization}/{project} | URL | Yes |
| [Private token](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops) | Password | No |
| Number of days since last build after which to consider pipelines inactive | Integer | No |
| Pipelines to ignore (regular expressions or pipeline names, use <folder>/<pipeline name> for pipelines in folders) | Multiple choice with addition | No |

### Unused CI-jobs from GitLab

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| GitLab instance URL | URL | Yes |
| [Project (name with namespace or id)](https://docs.gitlab.com/ee/user/project/) | String | Yes |
| [Private token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) | Password | No |
| Number of days without builds after which to consider CI-jobs unused. | Integer | No |

### Unused CI-jobs from Jenkins

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Number of days without builds after which to consider CI-jobs unused. | Integer | No |
| Jobs to ignore (regular expressions or job names, use <parent job name>/<child job name> for the names of nested jobs) | Multiple choice with addition | No |

### Violations from OJAudit

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL to an OJAudit report in XML format or to a zip with OJAudit reports in XML format | URL | Yes |
| URL to an OJAudit report in a human readable format | String | No |
| Username for basic authentication | String | No |
| Password for basic authentication | Password | No |
| Severities | Multiple choice | No |

### Violations from SonarQube

| Parameter | Type | Mandatory |
| :-------- | :--- | :-------- |
| URL | URL | Yes |
| [Private token](https://docs.sonarqube.org/latest/user-guide/user-token/) | Password | No |
| Project key | String | Yes |
| [Branch (only supported by commercial SonarQube editions)](https://docs.sonarqube.org/latest/branches/overview/) | String | No |
| [Severities](https://docs.sonarqube.org/latest/user-guide/issues/) | Multiple choice | No |
| [Types](https://docs.sonarqube.org/latest/user-guide/rules/) | Multiple choice | No |

