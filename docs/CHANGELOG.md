# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to *Quality-time* will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- The line "## <square-bracket>Unreleased</square-bracket>" is replaced by the ci/release.py script with the new release version and release date. -->

## [2.1.0] - [2020-03-29]

### Changed

- The collector wakes up every minute, collects measurement data if necessary, and then would pause for a minute. Changed to have the length of the pause depend on how long the data collection took so that the user does not have to wait too long for a new measurement after changing the configuration of a metric. Closes [#1100](https://github.com/ICTU/quality-time/issues/1100).
- Made the collector collect measurements in parallel to speed it up.

### Fixed

- The metrics "violations" and "suppressed violations" show zero violations (green status) even though the component has no SonarQube analysis. Fixes [#1090](https://github.com/ICTU/quality-time/issues/1090).

## [2.0.0] - [2020-03-08]

### Added

- Add a private token parameter to all sources that consists of JSON, XML, or HTML reports so that they can be retrieved from GitLab job artifacts. Closes [#1067](https://github.com/ICTU/quality-time/issues/1067). 
- Add a column to show the status (unconfirmed, confirmed, false positive, etc.) of security warnings, violations, etc. so that the user doesn't have to expand them to see the status. Closes [#1070](https://github.com/ICTU/quality-time/issues/1070).
- Show end date of technical debt in the measurement target column. Closes [#1072](https://github.com/ICTU/quality-time/issues/1072).
- Allow for accepting technical debt for a metric that has no sources or failing sources. Closes [#1076](https://github.com/ICTU/quality-time/issues/1076).
- Make date fields clearable. Closes [#1088](https://github.com/ICTU/quality-time/issues/1088).

### Fixed

- Don't store server-side generated report summaries in the database. The previously generated report summaries are removed from the database when the server starts, so starting may take longer than normal. Fixes [#1082](https://github.com/ICTU/quality-time/issues/1082).

### Removed

- Version 1 of the API has been removed. API version 1 was deprecated since Quality-time v1.3.0. Closes [#1051](https://github.com/ICTU/quality-time/issues/1051).
- Remove the Docker environment files and move the environment variables to the docker-compose files to simplify the compositions. Closes [#1063](https://github.com/ICTU/quality-time/issues/1063).

## [1.8.1] - [2020-03-03]

### Fixed

- When loading changes to show in the changelog, an internal server error could occur due to Mongo hitting its maximum buffer size for sorting. Add an index to the reports collection to prevent out of memory errors during sorting. Fixes [#1077](https://github.com/ICTU/quality-time/issues/1077).

## [1.8.0] - [2020-03-01]

### Changed

- Cache data model and other performance improvements. Note: the proxy settings for the data model API have been updated. See the Caddy configuration in the [docker-compose](../docker/docker-compose.yml). The order of the metric tabs has been changed. From left to right: first tab is the metric configuration, second the source(s) configuration, third the trend graph, and finally the tab(s) with details per source, if applicable. This makes it possible to lazily load the data for the trend graph and the details per source and show the tabs as soon as the data becomes available. Fixes [#1026](https://github.com/ICTU/quality-time/issues/1026).

### Added

- Allow for specifying variable parts of URLs in OWASP ZAP reports. This makes it possible to mark warnings as false positive even when parts of URLs change between runs of OWASP ZAP. Note: because the way Quality-time keeps track of the warnings has been changed, some OWASP ZAP warnings may need to be marked as false positive again. Closes [#1045](https://github.com/ICTU/quality-time/issues/1045).
- A new metric for measuring the number of (outdated) dependencies and a new source (Composer for PHP) that supports this metric were added. Closes [#1056](https://github.com/ICTU/quality-time/issues/1056).

## [1.7.1] - [2020-02-26]

### Fixed

- When using SonarQube as source for duplication, uncovered lines, or uncovered branches, the landing url would be incorrect. Fixes [#1044](https://github.com/ICTU/quality-time/issues/1044).
- The docker-compose YAML file now specifies that the proxy container should wait for the server and frontend containers to start. Fixes [#1046](https://github.com/ICTU/quality-time/issues/1046).
- The collector would fail if it could not write a timestamp to the health_check.txt file, e.g. due to a permission error. Fixed by writing the health_check.txt file to /tmp instead of the home directory of the default user and by catching and logging any OS errors that may occur. Fixes [#1057](https://github.com/ICTU/quality-time/issues/1057).

## [1.7.0] - [2020-02-22]

### Changed

- As the previous rendering component used by Quality-time is no longer maintained, it is replaced with a new component: [URL to PDF Microservice](https://github.com/alvarcarto/url-to-pdf-api). Quality-time uses the [ICTU fork](https://github.com/ICTU/url-to-pdf-api) that packages the service as a [Docker container](https://hub.docker.com/repository/docker/ictu/url-to-pdf-api).

### Fixed

- The new rendering component (see "Changed") shows the date in the correct format. Fixes [#1010](https://github.com/ICTU/quality-time/issues/1010).
- Show tags added by users in the tag drowdown so they don't have to keep typing added tags. Fixes [#1041](https://github.com/ICTU/quality-time/issues/1041).

### Removed

- Because the new rendering component (see "Changed") waits for network activity to stop before converting a report into PDF, the delay parameter is no longer needed.

## [1.6.2] - [2020-02-19]

### Fixed

- Use environment variables for both proxy host and port so the renderer uses the right URL to get the report. Fixes [#1031](https://github.com/ICTU/quality-time/issues/1031).
- OWASP ZAP warning keys were not always unique, causing trouble with marking them as false positive. Fixes [#1032](https://github.com/ICTU/quality-time/issues/1032).
- The Jenkins test report source would not correctly get the number of passed tests from aggregated test reports. Fixes [#1033](http://github.com/ICTU/quality-time/issues/1033).

## [1.6.1] - [2020-02-18]

### Fixed

- Don't refresh the change log when clicking the "Download report as pdf" button. Fixes [#1015](https://github.com/ICTU/quality-time/issues/1015).
- Make proxy port configurable. Fixes [#1018](https://github.com/ICTU/quality-time/issues/1018).
- Changes made to violations, issues, warnings, etc., such as marking them as false positive, were only visible in the metric change log and not in the change logs of the report, subject, and source. Note: because a change needed to be made to the database format to fix this, changes made to violations, issues, warnings, etc. before this release are not visible in the change log. Fixes [#1019](https://github.com/ICTU/quality-time/issues/1019).
- Anchore vulnerability keys are not always valid as JSON key, causing exceptions when the user tries to make changes to vulnerabilities. Hashing the keys prevents this issue. Fixes [#1023](https://github.com/ICTU/quality-time/issues/1023).
- The too many parameters, complex units, and long unit metrics with SonarQube as source would always report the percentage as zero. Fixes [#1027](https://github.com/ICTU/quality-time/issues/1027).

## [1.6.0] - [2020-02-12]

### Changed

- Several accessibility related changes, such as improved background colors, larger icons, more contrast, and labels for images. Closes [#1005](https://github.com/ICTU/quality-time/issues/1005).

### Fixed

- Changes made to violations, issues, warnings, etc., such as marking them as false positive, would not carry over after a failed measurement, forcing the user to make the same changes again. Fixes [#1007](https://github.com/ICTU/quality-time/issues/1007).

## [1.5.0] - [2020-02-09]

### Added

- Jenkins jobs with the JaCoCo Jenkins plugin can be used as source for the line and branch coverage metrics. Closes [#984](https://github.com/ICTU/quality-time/issues/984).
- Add Anchore Docker image vulnerability scan reports in JSON format as possible source for the security warnings metric. Closes [#1000](https://github.com/ICTU/quality-time/issues/1000).

### Changed

- Center the status column so that the trend graphs and the status icons have a bit more space between them. Closes [#985](https://github.com/ICTU/quality-time/issues/985).

### Fixed

- Sorting of metrics by measurement value, target value, and status did not work. Fixes [#981](https://github.com/ICTU/quality-time/issues/981).
- Exporting tag reports to PDF did not work. Fixes [#990](https://github.com/ICTU/quality-time/issues/990).
- When using Jira as source for the issues metric, the URL to Jira in the metrics table would not work properly. Fixes [#991](https://github.com/ICTU/quality-time/issues/991).

## [1.4.0] - [2020-01-31]

### Added

- Source parameter (URL's, user names, passwords, etc.) changes can be applied to different scopes: to just the source being edited or to multiple sources that have the same type and value as the one being edited. When applying the change to multiple sources, the user can change all sources (that have the same type and value) of a single metric, of a single subject, of a single report, or of all reports. Closes [#927](https://github.com/ICTU/quality-time/issues/927).
- Change logs show the users' avatars. Note that email addresses were not recorded in the change log until now, so avatars can only be shown for new changes. Closes [#948](https://github.com/ICTU/quality-time/issues/948).
- The delay for generating PDFs can be changed in the report title and can be passed to the API as parameter. Closes [#958](https://github.com/ICTU/quality-time/issues/958).

### Fixed

- The front end was still using one version 1 API. Fixes [#947](https://github.com/ICTU/quality-time/issues/947).
- Retrieving the change log would fail if not all recent changes had a change log entry. Fixes [#949](https://github.com/ICTU/quality-time/issues/949).
- After changing a value in the UI, Quality-time would briefly show the old value while it was updating the database. Fixes [#954](https://github.com/ICTU/quality-time/issues/954).
- Documentation API was not reachable. Fixes [#966](https://github.com/ICTU/quality-time/issues/966).

## [1.3.4] - [2020-01-15]

### Fixed

- Metrics with status unknown in the details view of the 'Metrics' metric did not show a question mark. Fixes [#935](https://github.com/ICTU/quality-time/issues/935).
- Check connection for all URL and credential parameters. Fixes [#944](https://github.com/ICTU/quality-time/issues/944).

## [1.3.3] - [2020-01-15]

### Fixed

- Subject cards in the report dashboard would not have a default subject title when the subject had no title. Fixes [#942](https://github.com/ICTU/quality-time/issues/942).

## [1.3.2] - [2020-01-15]

### Fixed

- Metrics with status unknown in the details view of the 'Metrics' metric did not show a question mark. Fixes [#935](https://github.com/ICTU/quality-time/issues/935).

## [1.3.1] - [2020-01-15]

### Fixed

- Adding sources did not work. Fixes [#939](https://github.com/ICTU/quality-time/issues/939).

## [1.3.0] - [2020-01-15]

### Added

- Added an option to exclude branches from being reported as unmerged when using GitLab or Azure DevOps as source for the unmerged branches metric. Closes [#879](https://github.com/ICTU/quality-time/issues/879).
- Sources can be reordered.
- Sources, metrics, subjects, and reports can be copied. Sources, metrics, and subjects can be moved across metrics, subjects, and reports. Implements [#881](https://github.com/ICTU/quality-time/issues/881).

### Changed

- The "hide metrics not requiring action" buttons now hide metrics in all subjects of a report at once. Closes [#907](https://github.com/ICTU/quality-time/issues/907).
- A new, simpler version of the API was introduced, version 2. Version 1 of the API is deprecated. See <http://quality-time.example.org/api/>, <http://quality-time.example.org/api/v1>, and <http://quality-time.example.org/api/v2>.

### Fixed

- Typo in metric pie chart tooltip ("Uknown"). Fixes [#857](https://github.com/ICTU/quality-time/issues/857).
- User documentation incorrectly said that the dashboard layout is persisted in the browser. It is kept in the database since version 1.0.0. Fixes [#860](https://github.com/ICTU/quality-time/issues/860).
- Add report title to subject names in tag reports so it is clear from which report each subject comes. Fixes [#880](https://github.com/ICTU/quality-time/issues/880).
- Tag reports could not be exported to PDF. Fixes [#885](https://github.com/ICTU/quality-time/issues/885).
- Prevent users from entering invalid percentages. Fixes [#888](https://github.com/ICTU/quality-time/issues/888).
- Fix Checkmarx landing URL. Fixes [#919](https://github.com/ICTU/quality-time/issues/919).
- Remove plaintext passwords from HTML. Fixes [#921](https://github.com/ICTU/quality-time/issues/921).
- Marking OWASP ZAP warnings as false positives did not work. Fixes [#922](https://github.com/ICTU/quality-time/issues/922).
- Remove private tokens from URLs logged by the collector. Fixes [#934](https://github.com/ICTU/quality-time/issues/934).

## [1.2.0] - [2019-12-10]

### Added

- If users have a [Gravatar](https://gravatar.com), it will be shown next to their username after they log in.
- REST API added for importing a complete report. Closes [#818](https://github.com/ICTU/quality-time/issues/818).
- Allow GitLab as source for the unused CI-jobs metric. Closes [#851](https://github.com/ICTU/quality-time/issues/851).

### Changed

- Open help urls in a new window or tab. Closes [#842](https://github.com/ICTU/quality-time/issues/842).

## [1.1.0] - [2019-12-03]

### Fixed

- Ignore Jira fields that have no number value when summing Jira issues for the ready user story points and manual test duration metrics. Fixes [#834](https://github.com/ICTU/quality-time/issues/834).

### Added

- Added a button (expand a report title to access it) to download a PDF version of a report. The PDF report can also be downloaded via the API: `http://www.quality-time.example.org/api/v1/report/<report_uuid>/pdf`.
Closes [#828](https://github.com/ICTU/quality-time/issues/828).
- Metric summary cards now have tooltips showing the number of metrics per status (target met, target not met, etc.). Closes [#838](https://github.com/ICTU/quality-time/issues/838).

### Changed

- Show the five most recent changes in the change log table initially so that the buttons below the change log table don't disappear off screen. Each click on the "load more changes" button still loads ten more changes. Closes [#836](https://github.com/ICTU/quality-time/issues/836).

## [1.0.0] - [2019-11-28]

### Fixed

- Users would not be notified of an expired session when trying to delete something while their session was expired. Fixes [#813](https://github.com/ICTU/quality-time/issues/813).
- Prevent double slashes in URLs to Jira issues. Fixes [#817](https://github.com/ICTU/quality-time/issues/817).
- Hiding metrics that do not require action did not work. Fixes [#824](https://github.com/ICTU/quality-time/issues/824).

### Added

- Store dashboard layouts on the server instead of in the local storage of the user's browser. Closes [#379](https://github.com/ICTU/quality-time/issues/379).

### Removed

- Removed deprecated metrics from metric types options. Closes [#826](https://github.com/ICTU/quality-time/issues/826).

## [0.20.0] - [2019-11-23]

### Fixed

- The Quality-time source still used port 5001 to access the Quality-time API. Fixes [#806](https://github.com/ICTU/quality-time/issues/806).

### Added

- Allow for filtering metrics by metric type and source type in the Quality-time source. Closes [#808](https://github.com/ICTU/quality-time/issues/808).

## [0.19.1] - [2019-11-19]

### Fixed

- Determining the encoding of large OWASP Dependency Check XML reports was very slow. Fixes [#803](https://github.com/ICTU/quality-time/issues/803).

## [0.19.0] - [2019-11-17]

### Fixed

- Use correct API URL when accessing Quality-time as source. Fixes [#791](https://github.com/ICTU/quality-time/issues/791).

### Added

- Metric for manual test execution added. Closes [#556](https://github.com/ICTU/quality-time/issues/556).
- Azure DevOps can now be a source for the failing jobs metric and the unused jobs metric. Closes [#638](https://github.com/ICTU/quality-time/issues/638).

## [0.18.0] - [2019-11-12]

### Fixed

- Add keep-alive messages to the server-sent events stream so it does not time out when there are no new measurements for a while. Fixes [#787](https://github.com/ICTU/quality-time/issues/787).

### Added

- In addition to a changelog per report, also keep a changelog for the reports overview. Closes [#746](https://github.com/ICTU/quality-time/issues/746).

## [0.17.0] - [2019-11-10]

### Fixed

- Make string input fields with suggestions clearable. Fixes [#772](https://github.com/ICTU/quality-time/issues/772).
- Open Axe CSV files in universal newline mode. Fixes [#777](https://github.com/ICTU/quality-time/issues/777).
- Prevent browser console traceback when switching to the sources tab of a metric. Fixes [#779](https://github.com/ICTU/quality-time/issues/779).

### Added

- More flexibility in configuring LDAP by introducing a `LDAP_SEARCH_FILTER` environment variable and replacing the `LDAP_LOOKUP_USER` variable by `LDAP_LOOKUP_USER_DN`. See the [LDAP section in the deployment document](https://github.com/ICTU/quality-time/blob/master/docs/DEPLOY.md#ldap). Closes [#774](https://github.com/ICTU/quality-time/issues/774).
- Logo for Axe. Closes [#778](https://github.com/ICTU/quality-time/issues/778).

## [0.16.1] - [2019-11-07]

### Fixed

- Ignoring Jenkins child jobs (jobs within pipelines) did not work. Fixes [#763](https://github.com/ICTU/quality-time/issues/763).
- Notifications from the server to the frontend about new measurements were broken after the introduction of the reverse proxy. Fixes [#765](https://github.com/ICTU/quality-time/issues/765).

## [0.16.0] - [2019-11-02]

### Added

- Allow for ignoring Jenkins jobs by name or regular expression. Closes [#747](https://github.com/ICTU/quality-time/issues/747).
- For sources that are comprised of static reports, it is now possible to specify a zip file with reports as URL. Quality-time will unzip the file before processing its contents as normal. So far, this has been implemented for Axe CSV reports, Bandit JSON reports, JaCoCo XML reports, JUnit XML reports, NCover HTML reports, OJAudit XML reports, OpenVAS XML reports, OWASP Dependency Check XML reports, OWASP ZAP XML reports, Performancetest-runner HTML reports, Pyup.io Safety JSON reports, and Robot Framework XML reports. Closes [#748](https://github.com/ICTU/quality-time/issues/748).

## [0.15.0] - [2019-10-30]

### Fixed

- The collector component would crash if an Azure DevOps source was unreachable. Fixes [#738](https://github.com/ICTU/quality-time/issues/738).
- Add a changelog entry when a user creates a report. Fixes [#742](https://github.com/ICTU/quality-time/issues/742).

### Changed

- Introduce a reverse proxy (Caddy) so that web frontend and API can both be accessed through the same port. Which is now port 80 by default. Fixes [#727](https://github.com/ICTU/quality-time/issues/727).

## [0.14.1] - [2019-10-24]

### Fixed

- Login problem solved for LDAP servers where a user bind must be done. Fixes [#734](https://github.com/ICTU/quality-time/issues/734).

## [0.14.0] - [2019-10-23]

### Fixed

- Toaster messages didn't disappear when clicked. Fixes [#717](https://github.com/ICTU/quality-time/issues/717).
- Don't crash the frontend after changing the type of a metric. Fixes [#718](https://github.com/ICTU/quality-time/issues/718).

### Added

- Immediate check of URL's accessibility added.  Closes [#478](https://github.com/ICTU/quality-time/issues/478).
- When measuring unmerged branches, have the metric landing URL point to the list of branches in GitLab or Azure DevOps. When measuring the source up-to-dateness of a folder or file in GitLab or Azure DevOps, have the metric landing URL point to the folder or file. Closes [#711](https://github.com/ICTU/quality-time/issues/711).
- When SonarQube is the source for a metric, users can now select the branch to use. Note that only the commercial editions of SonarQube support branch analysis. Closes [#712](https://github.com/ICTU/quality-time/issues/712).
- Subjects can be reordered. Expand a subject title to show the reordering buttons on the lower left-hand side of the subject title panel. The buttons allow one to move a subject to the top of the page, to the previous position, to the next position, and to the bottom of the page. Closes [#716](https://github.com/ICTU/quality-time/issues/716).
- Allow for filtering accessibility violations from Axe CSV files by impact level. Closes [#730](https://github.com/ICTU/quality-time/issues/730).

### Changed

- Use the ldap3 library instead of python_ldap. Closes [#679](https://github.com/ICTU/quality-time/issues/679).

### Removed

- The ability to use HQ quality reports as source was removed. Closes [#715](https://github.com/ICTU/quality-time/issues/715).

## [0.13.0] - [2019-10-20]

### Added

- Quality-time now counts the unmerged branches against the default branch in GitLab or Azure DevOps instead of assuming that the master branch is the default branch. Closes [#699](https://github.com/ICTU/quality-time/issues/699).

### Changed

- The "Size (LOC)" metric can now either count all lines of code or all non-commented lines of code. That means the "Size (Non-commented LOC)" metric is now deprecated. Closes [#644](https://github.com/ICTU/quality-time/issues/644).

### Fixed

- Allow for specifying an Azure DevOps repository by name. Fixes [#683](https://github.com/ICTU/quality-time/issues/683).

## [0.12.2] - [2019-10-16]

### Fixed

- Remove white space at the top of the page in printouts. Fixes [#685](https://github.com/ICTU/quality-time/issues/685).
- Don't crash when the user refreshes a report in the browser. Fixes [#692](https://github.com/ICTU/quality-time/issues/692).

### Changed

- Quality-time now uses Python 3.8 for the collector and server components. Closes [#684](https://github.com/ICTU/quality-time/issues/684).

## [0.12.1] - [2019-10-14]

### Fixed

- Allow for specifying the repository when using Azure DevOps as source for the "Source up-to-dateness" metric instead of assuming that the repository has the same name as the project. Fixes [#663](https://github.com/ICTU/quality-time/issues/663).
- Do not repeat the top menu bar in printouts, it overlaps with content. Fixes [#680](https://github.com/ICTU/quality-time/issues/680).

## [0.12.0] - [2019-10-11]

### Fixed

- Because Checkmarx does not immediately return detail information, Checkmarx measurements would alternate between measurements with and without detail information, resulting in a lot of measurements in the database. Fixed by not collecting detail information from Checkmarx anymore. Fixes [#670](https://github.com/ICTU/quality-time/issues/670).
- Sources that don't need to access the network ("Calendar", "Manual number", "Random number") would throw an exception. Fixes [#672](https://github.com/ICTU/quality-time/issues/672).
- NCover reports weren't parsed correctly. Fixes [#675](https://github.com/ICTU/quality-time/issues/675).

### Removed

- Quality-time no longer collects detail information about security warnings from Checkmarx; the Checkmarx API is too complex, resulting in fragile interaction between Quality-time and Checkmarx. See [#670](https://github.com/ICTU/quality-time/issues/672).

## [0.11.0] - [2019-10-07]

### Fixed

- Allow for specifying which test results (skipped, failed, errored, and/or passed) to count when using SonarQube as source for the "Tests" metric. Fixes [#634](https://github.com/ICTU/quality-time/issues/634).
- Store measurement values for each scale that a metric supports so that the graphs show correct information when the user changes the metric scale. Fixes [#637](https://github.com/ICTU/quality-time/issues/637).
- Do not stop contacting sources after receiving a 401 (Unauthorized) or 403 (Forbidden). Fixes [#652](https://github.com/ICTU/quality-time/issues/652).

### Added

- Add NCover coverage reports as source for the test coverage metrics. Closes [#635](https://github.com/ICTU/quality-time/issues/635).
- Add Azure DevOps as source for the "Tests" metric. Requires Azure Devops Server or Service 2019. Closes [#639](https://github.com/ICTU/quality-time/issues/639).
- Add Azure DevOps as source for the "Source up-to-dateness" metric. Closes [#640](https://github.com/ICTU/quality-time/issues/640).
- Add Azure DevOps as source for the "Unmerged branches" metric. Closes [#641](https://github.com/ICTU/quality-time/issues/641).
- Add percentage scale to the "Complex units", "Many parameters", "Long units", and "Suppressed violations" metrics. Closes [#645](https://github.com/ICTU/quality-time/issues/645).

## [0.10.2] - [2019-09-26]

### Fixed

- Measuring the source up-to-dateness of folders in GitLab did not work. Fixes [#626](https://github.com/ICTU/quality-time/issues/626).

## [0.10.1] - [2019-09-25]

### Fixed

- Measuring size (LOC), size (non-commented LOC), tests, and failed tests using SonarQube as source would fail with a parse error. Fixes [#623](https://github.com/ICTU/quality-time/issues/623).

## [0.10.0] - [2019-09-22]

### Added

- All metrics now have an explicit scale that's either fixed to "Count" or "Percentage", or that can be changed from "Count to "Percentage" and vice versa. Metrics whose scale can be changed: "Duplicated lines", "Metrics", "Test branch coverage", and "Test line coverage". Closes [#504](https://github.com/ICTU/quality-time/issues/504).
- Added a 'landing URL' parameter to some sources so Quality-time can refer users to a human readable version of a machine readable report. For example, you can add an HTML version of a JaCoCo report to a JaCoCo XML report source. Closes [#554](https://github.com/ICTU/quality-time/issues/554).

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
