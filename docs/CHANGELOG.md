# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to *Quality-time* will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- The line "## <square-bracket>Unreleased</square-bracket>" is replaced by the ci/release.py script with the new release version and release date. -->

## [Unreleased]

### Added

- Keep track of changes made by users in a change log. The change log for a report can be viewed by expanding the report title. The change log for a subject can be viewed by expanding the subject title. The change logs for metric and their sources be viewed by expanding the metric. Closes [#285](https://github.com/ICTU/quality-time/issues/285).
- When the user session is expired (after 24 hours) log out the user and notify them of the expired session. Closes [#373](https://github.com/ICTU/quality-time/issues/373).
- Added a metric for measuring the duration of manual tests. Added Jira as default source for the metric. Closes [#481](https://github.com/ICTU/quality-time/issues/481).

### Fixed

- When using OWASP ZAP reports as source for the security warnings metric, report on the number of "instances" instead of "alert items". Fixes [#467](https://github.com/ICTU/quality-time/issues/467).
- The performancetest-runner now uses "scalability" instead of "ramp-up" as name for the scalability measurement. Closes [#480](https://github.com/ICTU/quality-time/issues/480).

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
