# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to *Quality-time* will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- The line "## <square-bracket>Unreleased</square-bracket>" is replaced by the ci/release.py script with the new release version and release date. -->

## [Unreleased]

### Fixed

- Measuring size (LOC), size (non-commented LOC), tests, and failed tests using SonarQube as source would fail with a parse error. Fixes [#623](https://github.com/ICTU/quality-time/issues/623). 

## [0.10.0] - [2019-09-22]

### Added

- All metrics now have an explicit scale that's either fixed to "Count" or "Percentage", or that can be changed from "Count to "Percentage" and vice versa. Metrics whose scale can be changed: "Duplicated lines", "Metrics", "Test branch coverage", and "Test line coverage". Closes [#504](https://github.com/ICTU/quality-time/issues/504).
- Added a 'landing url' parameter to some sources so Quality-time can refer users to a human readable version of a machine readable report. For example, you can add an HTML version of a JaCoCo report to a JaCoCo XML report source. Closes [#554](https://github.com/ICTU/quality-time/issues/554).

## [0.9.1] - [2019-09-10]

### Fixed

- To prevent reporting Checkmarx internal server errors to users when reports are unexpectedly unavailable, don't immediately remove a Checkmarx report after reading it, but silently ignore a removed report and create a new one. Fixes [#468](https://github.com/ICTU/quality-time/issues/468).
- Prevent locked accounts by not contacting a source again after receiving a 401 (unauthorized) or 403 (forbidden) HTTP status, until the metric's configuration changes. Fixes [#604](https://github.com/ICTU/quality-time/issues/604).

## [0.9.0] - [2019-09-06]

### Added

- The direction of metrics is now configurable. The direction of a metric determines whether smaller measurements are better, or bigger measurements are better. This means that the "number of tests" metric, with its direction reversed, can now also be used to measure the number of failing tests. The "failing tests" metric is deprecated. Closes [#552](https://github.com/ICTU/quality-time/issues/552).
- Metrics can be reordered. Expand a metric to show the reordering buttons on the lower left-hand side of the metric details. The buttons allow one to move a metric to the top of the table, to the previous row, to the next row, and to the bottom of the table. Closes [#585](https://github.com/ICTU/quality-time/issues/585).

### Fixed

- Checkmarx internal server error solved. Fixes [#468](https://github.com/ICTU/quality-time/issues/468).
- Use a consistent style for labels of input fields. Fixes [#579](https://github.com/ICTU/quality-time/issues/579).
- Added Quality-time logo to the Quality-time source. Fixes [#580](https://github.com/ICTU/quality-time/issues/580).
- When adding HQ as source for the accessibility metric, show the URL and metric id parameters. Fixes [#587](https://github.com/ICTU/quality-time/issues/587).
- The layout of the reports overview dashboard would be reset after visiting a tag report. Fixes [#588](https://github.com/ICTU/quality-time/issues/588).
- Tag report donut charts were always white. Fixes [#589](https://github.com/ICTU/quality-time/issues/589).

## [0.8.2] - [2019-08-28]

### Fixed

- Prevent web browsers from automatically filling in username and password in the source configuration tab. Fixes [#574](https://github.com/ICTU/quality-time/issues/574).

## [0.8.1] - [2019-08-28]

### Fixed

- Changing the subject type now changes the subject name if the default subject name has not been overridden. Fixes [#553](https://github.com/ICTU/quality-time/issues/553).
- When a user changes a password field, don't show the old password in the change log unmasked. Fixes [#565](https://github.com/ICTU/quality-time/issues/565).
- Use <= and >= for the metric direction in the metric tables instead of < and >. Fixes [#567](https://github.com/ICTU/quality-time/issues/567).

## [0.8.0] - [2019-08-23]

### Added

- Add meta metrics and the ability to add *Quality-time* itself as source for the meta metrics. Closes [#337](https://github.com/ICTU/quality-time/issues/337). 
- Accessibility metric for Axe report source added. Closes [#338](https://github.com/ICTU/quality-time/issues/338).

### Fixed

- Don't use the unicode characters for <= and >= in the source code; it caused problems on Windows. Fixes [#558](https://github.com/ICTU/quality-time/issues/558).

## [0.7.1] - [2019-08-18]

### Fixed

- When generating keys for OWASP ZAP security warnings, strip any hashes from the application urls to ensure the keys are stable. Fixes [#541](https://github.com/ICTU/quality-time/issues/541).
- In addition to version 2.0 also support version 2.1 and 2.2 of the OWASP Dependency Check XML format. Fixes [#543](https://github.com/ICTU/quality-time/issues/543).

## [0.7.0] - [2019-08-14]

### Added

- Users can now select a suggestion and edit it in input fields with suggestions. Closes [#197](https://github.com/ICTU/quality-time/issues/197).
- Users can now login with both their canonical LDAP name as well as with their LDAP user id. Closes [#492](https://github.com/ICTU/quality-time/issues/492).
- Allow for using (a safe subset of) HTML and URL's in metric comment fields. Closes [#511](https://github.com/ICTU/quality-time/issues/511).
- Added OWASP Dependency Check Jenkins plugin as possible source for the security warnings metric. Closes [#535](https://github.com/ICTU/quality-time/issues/535).

### Fixed

- Break long lines in OpenVAS security warning description to keep the metrics table from becoming very wide. Fixes [#452](https://github.com/ICTU/quality-time/issues/452).
- Break long urls in source error messages to keep the metrics table from becoming very wide. Fixes [#531](https://github.com/ICTU/quality-time/issues/531).
- Don't try to retrieve more work items from Azure DevOps than allowed. Fixes [#532](https://github.com/ICTU/quality-time/issues/532).
- Return a parse error if OWASP dependency report XML reports don't contain the expected root tag instead of reporting zero issues. Fixes [#536](https://github.com/ICTU/quality-time/issues/536).

## [0.6.0] - [2019-08-11]

### Added

- Keep track of changes made by users in a change log. The change log for a report can be viewed by expanding the report title. The change log for a subject can be viewed by expanding the subject title. The change logs for metric and their sources be viewed by expanding the metric. Closes [#285](https://github.com/ICTU/quality-time/issues/285).
- When the user session is expired (after 24 hours) log out the user and notify them of the expired session. Closes [#373](https://github.com/ICTU/quality-time/issues/373).
- Added a metric for measuring the duration of manual tests. Added Jira as default source for the metric. Closes [#481](https://github.com/ICTU/quality-time/issues/481).

### Fixed

- When using OWASP ZAP reports as source for the security warnings metric, report on the number of "instances" instead of "alert items". Fixes [#467](https://github.com/ICTU/quality-time/issues/467).
- Don't wait 15 minutes before trying to access a requested Checkmarx SAST XML report, but try again after one minute. Partial fix for [#468](https://github.com/ICTU/quality-time/issues/468).
- The performancetest-runner now uses "scalability" instead of "ramp-up" as name for the scalability measurement. Closes [#480](https://github.com/ICTU/quality-time/issues/480).
- OJAudit XML files may contain duplicate violations (i.e. same message, same severity, same model, same location, same everything) which led to problems in the user interface. Fixed by merging multiple duplication violations and adding a count field to the violations. Fixes [#515](https://github.com/ICTU/quality-time/issues/515).
- Use Jenkins job timestamp for the source up-to-dateness metric if the Jenkins test report doesn't contain timestamps in the test report itself. Fixes [#517](https://github.com/ICTU/quality-time/issues/517).
- Stop sorting metrics when the user adds a new metric to prevent it from jumping around due to the sorting. Fixes [#518](https://github.com/ICTU/quality-time/issues/518).

## [0.5.1] - [2019-07-18]

### Fixed

- The Trello parameter "lists to ignore" was not displayed properly. Fixes [#471](https://github.com/ICTU/quality-time/issues/471).
- The number of issues would not be measured if the source was Jira. Fixes [#475](https://github.com/ICTU/quality-time/issues/475).

## [0.5.0] - [2019-07-16]

### Added

- Added Pyup.io Safety JSON reports as possible source for the security warnings metric. Closes [#450](https://github.com/ICTU/quality-time/issues/450).
- Added Bandit JSON reports as possible source for the security warnings metric and the source up-to-dateness metric. Closes [#454](https://github.com/ICTU/quality-time/issues/454).
- Only measure metrics that have all mandatory parameters supplied. Closes [#462](https://github.com/ICTU/quality-time/issues/462).

### Fixed

- Add performance test stability and scalability metrics to the example report. Fixes [#447](https://github.com/ICTU/quality-time/issues/447).
- Set up a new LDAP connection for each authentication in an attempt to prevent a "Broken pipe" between Quality-time and the LDAP-server. Fixes [#469](https://github.com/ICTU/quality-time/issues/469).

## [0.4.1] - [2019-07-08]

### Fixed

- Frontend can't reach server.

## [0.4.0] - [2019-07-07]

### Changed

- Run server on port 5001 instead of 8080 to reduce chances of interfering with other applications.
- Allow for deployments where the different components all have the same hostname, e.g. quality-time.example.org, and only the ports differ.

## [0.3.0] - [2019-07-05]

### Added

- Metric for performancetest duration added. Closes [#401](https://github.com/ICTU/quality-time/issues/401).
- Metric for performancetest stability added. Closes [#433](https://github.com/ICTU/quality-time/issues/433).
- Metric for performance scalability added. Closes [#434](https://github.com/ICTU/quality-time/issues/434).
- [Performancetest-runner](https://github.com/ICTU/performancetest-runner) reports can now be used as metric source for the tests and failed tests metrics. Closes [#402](https://github.com/ICTU/quality-time/issues/402).

## [0.2.3] - [2019-07-01]

### Fixed

- Time travelling to a date before any report existed would throw an exception on the server. Fixes [#416](https://github.com/ICTU/quality-time/issues/416).
- Trend graphs would be too tall and overlap with the next metric. Fixes [#420](https://github.com/ICTU/quality-time/issues/420).
- When clicking the report date field in the menu bar, the calendar popup would be displayed at the wrong location before popping up at the right location. Fixes [#424](https://github.com/ICTU/quality-time/issues/424).

## [0.2.2] - [2019-06-28]

### Fixed

- Version number was missing in the footer of the frontend. Fixes [#410](https://github.com/ICTU/quality-time/issues/420).

## [0.2.1] - [2019-06-26]

### Fixed

- Work around a limitation of the Travis configuration file. The deploy script does not allow sequences, which is surprising since scripts in other parts of the Travis configuration file do allow sequences. See [https://github.com/travis-ci/dpl/issues/673](https://github.com/travis-ci/dpl/issues/673).

## [0.2.0] - [2019-06-26]

### Added

- Release Docker containers from [Travis CI](https://travis-ci.org/ICTU/quality-time) to [Docker Hub](https://cloud.docker.com/u/ictu/repository/list?name=quality-time&namespace=ictu).

## [0.1.0] - [2019-06-24]

### Added

- Initial release consisting of a metric collector, a web server, a frontend, and a database component.
