# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to *Quality-time* will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- The line "## <square-bracket>Unreleased</square-bracket>" is replaced by the release/release.py script with the new release version and release date. -->

## [Unreleased]

### Fixed

- If a metric did not have sources (with all mandatory parameters configured), the status of issues would not be collected. Fixes [#3221](https://github.com/ICTU/quality-time/issues/3221).
- Allow for specifying zip files as Gatling source. Fixes [#3226](https://github.com/ICTU/quality-time/issues/3226).
- Remove spaces from file paths in OWASP Dependency Check security warnings before applying the regular expressions to remove variable parts from the file paths. Unfortunately, this may change the key of some OWASP Dependency Check security warnings, causing the status (false positive, won't fix, etc.) of the warning in *Quality-time* to be lost. Fixed as part of [#3259](https://github.com/ICTU/quality-time/issues/3259).

### Changed

- Use the 'number of dates' menu (now located in the settings panel, see #3248 below) to switch between what used to called 'trend' view (multiple dates) and 'details' view (one date). If you export PDFs via the API, you may need to change the URL parameters: `trend_table_nr_dates` is now called `nr_dates` and `trend_table_internal` is now called `date_interval`. Also, `trend_table_interval` was a number of weeks, `date_interval` is in days. See the [documention on PDF-exports via the API](https://quality-time.readthedocs.io/en/latest/usage.html#via-the-api). Closes [#3206](https://github.com/ICTU/quality-time/issues/3206).
- Make the subject title and header row of subject tables 'sticky', meaning that the title and header rows stay visible until the whole table scrolls off-screen. Closes [#3219](https://github.com/ICTU/quality-time/issues/3219).
- Move the contents of the hamburger menu to a settings panel that can be brought into view via the menu bar. Closes [#3248](https://github.com/ICTU/quality-time/issues/3248).

### Added

- Add a menu item to the settings panel to collapse all expanded metrics at once. Closes [#3133](https://github.com/ICTU/quality-time/issues/3133).
- Show the key of OWASP Dependency Check security warnings in the measurement entity details to allow for verification of the regular expressions used to remove variable parts from file paths. Closes [#3259](https://github.com/ICTU/quality-time/issues/3259).

## v3.31.0 - 2022-01-13

### Fixed

- The dropdown menu for determining the scope of parameter changes (Apply change to source/metric/etc.) would not appear when clicking the "Apply change to" part of the label. Fixes [#3112](https://github.com/ICTU/quality-time/issues/3112).
- OWASP ZAP uses a non-standard versioning scheme (D-year-month-day) for its weekly versions, be prepared. Fixes [#3117](https://github.com/ICTU/quality-time/issues/3117).
- Show a more informative error message if no merge request information can be retrieved from GitLab for the 'merge requests' metric. Fixes [#3166](https://github.com/ICTU/quality-time/issues/3166).
- The hamburger submenu's were only partially clickable. Also make the hamburger menu popup on hover for better discoverability. Fixes [#3181](https://github.com/ICTU/quality-time/issues/3181).
- When sorting metrics by status, order by how urgently action is required: 'unknown' (white), 'target not met' (red), 'near target met' (yellow), 'technical debt accepted' (grey), 'target met' (green). Fixes [#3184](https://github.com/ICTU/quality-time/issues/3184).
- Reset the edit scope of source parameters to 'source' after each edit. Fixes [#3198](https://github.com/ICTU/quality-time/issues/3198).

### Changed

- Use users' full name instead of their username in the change log so it's easier to see who changed what. Closes [#2930](https://github.com/ICTU/quality-time/issues/2930).
- Improved tooltips for the measurement column in the metrics details table. Closes [#3171](https://github.com/ICTU/quality-time/issues/3171).

### Added

- Show the source, comment, issues, and tags columns in the metric trend view. Closes [#2414](https://github.com/ICTU/quality-time/issues/2414), [#3203](https://github.com/ICTU/quality-time/issues/3203), [#3037](https://github.com/ICTU/quality-time/issues/3037), and [#3202](https://github.com/ICTU/quality-time/issues/3202).
- Allow for copying permanent links to metrics, subjects, and reports via the new 'Share' tabs. Closes [#2925](https://github.com/ICTU/quality-time/issues/2925).
- Allow for adding comments to the report overview, to reports, and to subjects. Expand the title of the report overview, report, or subject to enter comments. Entered comments are shown below the title of the report overview, report, or subject. Simple HTML (headers, bold, italic, links, etc.) is allowed. Closes [#2926](https://github.com/ICTU/quality-time/issues/2926).
- Explain in the [documentation](https://quality-time.readthedocs.io/en/latest/usage.html#via-the-api) how to include the correct report URL in the footer when exporting reports to PDF via the API. Closes [#2954](https://github.com/ICTU/quality-time/issues/2954).
- In addition to the 90th percentile, also allow for evaluating the 95th and 99th percentile transaction response time when using JMeter CSV or JSON as source for the 'slow transactions' metric. Closes [#3084](https://github.com/ICTU/quality-time/issues/3084).
- Add support for Gatling as source for the 'slow transactions', 'tests', 'performancetest duration', 'source up-to-dateness', and 'source version' metrics. Closes [#3085](https://github.com/ICTU/quality-time/issues/3085), [#3086](https://github.com/ICTU/quality-time/issues/3086), [#3087](https://github.com/ICTU/quality-time/issues/3087), [#3088](https://github.com/ICTU/quality-time/issues/3088), and [#3089](https://github.com/ICTU/quality-time/issues/3089).
- The dependencies in OWASP Dependency Check reports do not always have unique keys. However, *Quality-time* needs dependencies to be uniquely identifiable to detect whether the dependencies change between measurements. If needed, *Quality-time* generates keys for dependencies itself, based on the dependencies' file paths. If for some reason the file path changes between measurements, however, the key changes as well. To remediate this, allow for ignoring parts of file paths using regular expressions, when measuring 'dependencies' or 'security warnings' with OWASP Dependency Check as source. Closes [#3099](https://github.com/ICTU/quality-time/issues/3099).
- After changing multiple source parameters at once, show a toaster message with the number of sources updated. Closes [#3137](https://github.com/ICTU/quality-time/issues/3137).
- In the metric trend view (selectable via the hamburger menu), allow for setting the interval between dates to one day, in addition to one or more weeks. Closes [#3182](https://github.com/ICTU/quality-time/issues/3182).
- Allow for sorting the metrics when displayed in the trend view. Closes [#3207](https://github.com/ICTU/quality-time/issues/3207).

### Removed

- Don't hide the tag pie charts in the dashboard when the user hides the tags column: it's not obvious that hiding the tags column would have that effect. Closes [#3202](https://github.com/ICTU/quality-time/issues/3202).

## v3.30.2 - 2021-12-19

### Fixed

- A bug in the Quality-time API would cause the sparkline graphs to draw the recent measurements as if they all happened on the current day and cause the notifier to send notifications to MS Teams every minute. Fixes [#3071](https://github.com/ICTU/quality-time/issues/3071) and [#3073](https://github.com/ICTU/quality-time/issues/3073).

## v3.30.1 - 2021-12-17

### Fixed

- The notifier would crash. Fixes [#3065](https://github.com/ICTU/quality-time/issues/3065).

## v3.30.0 - 2021-12-16

### Fixed

- Don't show a cursor in input fields when they are read only, e.g. because the user hasn't logged in, is time traveling, or is viewing a tag report. Fixes [#2933](https://github.com/ICTU/quality-time/issues/2933).
- When time traveling, *Quality-time* would show deleted reports after their deletion date. Fixes [#2997](https://github.com/ICTU/quality-time/issues/2997).
- Zero values were not shown in the measurement detail tables. Fixes [#3008](https://github.com/ICTU/quality-time/issues/3008).

### Added

- Support [JMeter CSV output](https://jmeter.apache.org/usermanual/generating-dashboard.html#saveservice_requirements) as source for the 'performance test duration', 'slow transactions', 'tests', and 'source up-to-dateness' metrics. Closes [#2965](https://github.com/ICTU/quality-time/issues/2965), [#2966](https://github.com/ICTU/quality-time/issues/2966), [#2967](https://github.com/ICTU/quality-time/issues/2967) and [#2010](https://github.com/ICTU/quality-time/issues/3010).

## v3.29.0 - 2021-12-03

### Fixed

- Time travel was broken: *Quality-time* would show the current measurement value regardless of the date selected. Fixes [#2958](https://github.com/ICTU/quality-time/issues/2958).

### Changed

- More flexible parsing of Axe-core JSON files to account for the different ways people aggregate Axe-core output into one JSON file, for the 'source up-to-dateness' and 'version' metrics. Closes [#2910](https://github.com/ICTU/quality-time/issues/2910).
- Upgrade MongoDB to version 4.4. **Note that to upgrade to this version of *Quality-time* your previous version needs to be at least version 3.24.0**. Closes [#2911](https://github.com/ICTU/quality-time/issues/2911).

### Added

- Support JMeter JSON output as source for the 'slow transactions' and 'tests' metrics. Closes [#2766](https://github.com/ICTU/quality-time/issues/2766), [#2936](https://github.com/ICTU/quality-time/issues/2936), and [#2950](https://github.com/ICTU/quality-time/issues/2950).

## v3.28.0 - 2021-11-22

### Fixed

- Use the correct report URL in the footer of reports exported to PDF. Fixes [#2750](https://github.com/ICTU/quality-time/issues/2750).
- The ARIA (Rich Internet Application Accessibility) label of status pie charts would report the wrong number of red metrics. Fixes [#2779](https://github.com/ICTU/quality-time/issues/2779).
- The security warnings in OWASP ZAP reports do not have unique keys. However, *Quality-time* needs security warnings to be uniquely identifiable to detect whether the list of warnings changes between measurements. Therefore, *Quality-time* generates keys for OWASP ZAP security warnings itself. Unfortunately, the key that *Quality-time* generated, was not guaranteed to be unique. Fixes [#2852](https://github.com/ICTU/quality-time/issues/2852).
- Multiple edits with the same description would show up as one entry in the changelog. Fixes [#2893](https://github.com/ICTU/quality-time/issues/2893).
- *Quality-time* was using a broken and deprecated API endpoint to collect data for the 'metrics' metric. Fixes [#2897](https://github.com/ICTU/quality-time/issues/2897).

### Added

- Allow for using HTML reports generated by [axe-html-reporter](https://www.npmjs.com/package/axe-html-reporter) as source for the accessibility violations metric. Closes [#2813](https://github.com/ICTU/quality-time/issues/2813).

## v3.27.0 - 2021-10-25

### Fixed

- Use ❯ instead of / to create subject breadcrumbs in tag reports, so they are consistent with breadcrumbs in copy and move button dropdowns.
- Prevent "Warning: `Infinity` is an invalid value for the `width` css style property." messages in the console log.
- Prevent "Error: Problem parsing d="M-2592.670630208333,NaNL-2592.670630208333,..." messages in the console log. These messages were caused by trying to create a sparkline graph for the source version metric. Fixes [#2663](https://github.com/ICTU/quality-time/issues/2663).
- Use submenus in the hamburger menu to make it shorter and prevent menu items from being drawn off-screen. Fixes [#2666](https://github.com/ICTU/quality-time/issues/2666).
- Measurement entities marked as false positive or fixed weren't being crossed out. Fixes [#2739](https://github.com/ICTU/quality-time/issues/2739).

### Changed

- Performance improvements. Closes [#2692](https://github.com/ICTU/quality-time/issues/2692) and [#2695](https://github.com/ICTU/quality-time/issues/2695).
- Make the metric tables use less vertical space when in details view. This allows for more metrics to fit on the screen. It also makes the vertical space used by the details view and the trend view more similar.
- Use a lightning bolt icon for metrics that don't meet their target value, to suggest danger and/or risk. The previously used x-shaped icon is typically associated with closing things, and thus less appropriate.

### Removed

- Remove the box around dashboards to reduce visual clutter.
- Remove the 'scroll to dashboard' button; it's not really needed (users can simply use the home button) and an unusual feature.

## v3.26.0 - 2021-10-04

### Changed

- Use tabs to better organize the settings that are accessible via expandable headers. Also add icons to the tabs.
- More flexible parsing of Axe-core JSON files to account for the different ways people aggregate Axe-core output into one JSON file. Closes [#2657](https://github.com/ICTU/quality-time/issues/2657).

### Added

- Make metrics expandable in the metric trend table view so metrics and sources can be configured in the trend table view as well as in the metric detail view. Closes [#2176](https://github.com/ICTU/quality-time/issues/2176)
- Allow for adding issues to metrics to e.g. track progress on resolving technical debt. Closes [#2215](https://github.com/ICTU/quality-time/issues/2215) and [#2628](https://github.com/ICTU/quality-time/issues/2628).
- Make report title in the footer a URL to the report itself. Closes [#2532](https://github.com/ICTU/quality-time/issues/2532).
- Sentiment metric. Closes [#2533](https://github.com/ICTU/quality-time/issues/2533).
- Add [documentation on how to move *Quality-time* from location to another](https://quality-time.readthedocs.io/en/latest/deployment.html#moving-quality-time). Closes [#2538](https://github.com/ICTU/quality-time/issues/2538).

## v3.25.0 - 2021-09-06

### Fixed

- Don't use the UUIDs generated by OpenVAS to compare OpenVAS security warnings because they are not stable across OpenVAS scans. Fixes [#2544](https://github.com/ICTU/quality-time/issues/2544).
- Don't mention the admin user in the "Trying it out" section of the documentation as [the admin user currently doesn't exist in the osixia/docker-openldap image](https://github.com/osixia/docker-openldap/issues/555). Fixes [#2565](https://github.com/ICTU/quality-time/issues/2565).

### Added

- Add pagination support for Jira so queries that result in more than 500 results are retrieved completely. Closes [#2386](https://github.com/ICTU/quality-time/issues/2386).
- Allow Robot Framework reports as source for the test cases metric. Closes [#2534](https://github.com/ICTU/quality-time/issues/2534).
- Allow Jenkins test reports as source for the test cases metric. Closes [#2543](https://github.com/ICTU/quality-time/issues/2543).

### Removed

- Don't send notifications about metrics having the same status for three weeks: it's not useful enough. Closes [#2529](https://github.com/ICTU/quality-time/issues/2529).

## v3.24.0 - 2021-08-23

### Fixed

- In addition to "low", "medium", "high", and "critical", the OWASP Dependency Check may report vulnerabilities with severity "moderate". Allow for using this severity for filtering vulnerabilities. Fixes [#2337](https://github.com/ICTU/quality-time/issues/2337).
- When measuring 'missing metrics', count missing metric types per subject instead of per report. Fixes [#2352](https://github.com/ICTU/quality-time/issues/2352).
- Add subject name to metrics in MS Teams notifications, so it's clear which metric changed status when different subjects have metrics with the same name. Fixes [#2353](https://github.com/ICTU/quality-time/issues/2353).
- After copying a metric, subject, or report, the same item could not be copied again. Fixes [#2364](https://github.com/ICTU/quality-time/issues/2364).
- After reloading a report, edit controls are shown even when the user has no edit permission. Fixes [#2373](https://github.com/ICTU/quality-time/issues/2373).
- The security warnings in OWASP ZAP reports do not have unique keys. However, *Quality-time* needs security warnings to be uniquely identifiable to detect whether the list of warnings changes between measurements. Therefore, *Quality-time* generates keys for OWASP ZAP security warnings itself. Unfortunately, the key that *Quality-time* generated, was not guaranteed to be unique. Fixes [#2429](https://github.com/ICTU/quality-time/issues/2429).
- JUnit XML files may have empty test suites, be prepared. Fixes [#2507](https://github.com/ICTU/quality-time/issues/2507).

### Added

- When measuring merge requests with GitLab Premium as source, the merge requests can be filtered by approval state. Closes [#1979](https://github.com/ICTU/quality-time/issues/1979).
- Include the key of Jira issues in the measurement details of the 'issues', 'manual test duration', 'manual test execution', and 'user story points' metrics. Prepares for [#2139](https://github.com/ICTU/quality-time/issues/2139).
- Add a test cases metric to count the number of test cases that have been executed, possibly limited to passed, failed, and/or skipped test cases. See the [user manual](usage.md#test-cases). Closes [#2139](https://github.com/ICTU/quality-time/issues/2139).
- Include the tests from TestNG XML reports in the measurement details of the 'tests' metric. Closes [#2388](https://github.com/ICTU/quality-time/issues/2388).
- The API has a new endpoint in REST style, `/api/v3/report`, to retrieve all reports.
- Publish *Quality-time* [documentation at Read the Docs](https://quality-time.readthedocs.io/en/latest/index.html).

### Changed

- The API endpoint `/api/v3/report/{report_uuid}` now also supports tag uuid's.
- Use [react-toastify](https://www.npmjs.com/package/react-toastify) for toast messages instead of the unmaintained [react-semantic-toasts](https://www.npmjs.com/package/react-semantic-toasts). Fixes [#2290](https://github.com/ICTU/quality-time/issues/2290).
- Use [semantic-ui-calendar-react-17](https://www.npmjs.com/package/semantic-ui-calendar-react-17) for date pickers instead of the unmaintained [semantic-ui-calendar-react](https://www.npmjs.com/package/semantic-ui-calendar-react). Fixes [#2291](https://github.com/ICTU/quality-time/issues/2291).

### Deprecated

- The API endpoint `/api/v3/reports` is deprecated. Use `/api/v3/reports_overview` and `/api/v3/report` instead.
- The API endpoint `/api/v3/tag_report` is deprecated. Use `/api/v3/report/{report_uuid}` instead.

### Removed

- Remove the search function as it is very limited and users indicate they don't use it. Closes [#2305](https://github.com/ICTU/quality-time/issues/2305).

## v3.23.3 - 2021-06-29

### Fixed

- Work around a [bug in aiohttp](https://github.com/aio-libs/aiohttp/issues/2217) that causes GitLab connections to hang and timeout when the GitLab data is paginated. Fixes [#2231](https://github.com/ICTU/quality-time/issues/2231).
- The report dashboard layout couldn't be changed. Fixes [#2305](https://github.com/ICTU/quality-time/issues/2305).

## v3.23.2 - 2021-06-17

### Fixed

- To prevent overloading *Quality-time*, the collector now measures a limited number (30 by default) of metrics each time it wakes up. If there are more than 30 metrics to measure, these get postponed to the next wakeup. To compensate, the collector wakes up more often (every 20 seconds instead of every 60 seconds) to see whether metrics need measuring. Metrics recently edited by users get priority.
- Fix a performance regression in the collector component, introduced in v3.23.0.
- Allow for importing reports with metrics that have no scale or addition attribute. Fixes [#2262](https://github.com/ICTU/quality-time/issues/2262).

## v3.23.1 - 2021-06-13

### Fixed

- Allow for importing reports with metrics that have no tags. Fixes [#2262](https://github.com/ICTU/quality-time/issues/2262).

## v3.23.0 - 2021-06-09

### Fixed

- Allow for importing reports with unencrypted credentials. Fixes [#2238](https://github.com/ICTU/quality-time/issues/2238).
- Axe CSV files may contain duplicate accessibility violations. These duplicated violations couldn't be marked as false positive, won't fix, etc. Fixed by ignoring duplicate violations. Fixes [#2232](https://github.com/ICTU/quality-time/issues/2232).

### Added

- Add 'Missing metrics' metric. Closes [#1477](https://github.com/ICTU/quality-time/issues/1477).

### Removed

- Drop support for Wekan source for Issue and Source-up-to-dateness metrics. Closes [#2229](https://github.com/ICTU/quality-time/issues/2229).

## v3.22.0 - 2021-05-26

### Fixed

- When the collector posts new measurements to the server, the server looks up previous measurements in the database to see if the measurement value has changed. This lookup was slow due to a missing index on the measurements collection. Fixes [#2155](https://github.com/ICTU/quality-time/issues/2155).
- Edit controls were not hidden or made read-only in the UI when time traveling and after logout. Fixes [#2170](https://github.com/ICTU/quality-time/issues/2170).
- Measuring security warnings with Anchore as source would throw a parse error if the source was an unzipped Anchore JSON file. Fixes [#2177](https://github.com/ICTU/quality-time/issues/2177).
- When all users are allowed to edit reports, no users would be able to edit measurement entities to mark them as false positive, fixed, etc. Fixes [#2179](https://github.com/ICTU/quality-time/issues/2179).

### Removed

- Since subjects have a trend table view, there is little added value in also having a trend table per metric. Remove the trend table view for individual metrics. Closes [#2174](https://github.com/ICTU/quality-time/issues/2174).

### Added

- Add support for Robot Framework v4 XML files. Closes [#2136](https://github.com/ICTU/quality-time/issues/2136).

## v3.21.0 - 2021-04-25

### Fixed

- Prevent (rare) crashes of the UI when switching tabs in the metric details. Fixes [#1873](https://github.com/ICTU/quality-time/issues/1873).
- Don't assume that because GitLab returns jobs sorted by ID, they are also sorted by date. Fixes [#2036](https://github.com/ICTU/quality-time/issues/2036).
- Prevent timeouts when collecting failed CI-jobs or unused CI-jobs from GitLab by removing the limit on open connections. Fixes [#2037](https://github.com/ICTU/quality-time/issues/2037).
- *Quality-time* wouldn't recognize zip files in URLs with query strings (e.g. `https://git.example.org/foo.zip?job=bar`). Fixes [#2057](https://github.com/ICTU/quality-time/issues/2057).

### Added

- Separate permissions for editing measured entities. Closes [1842](https://github.com/ICTU/quality-time/issues/1842).
- When measuring accessibility violations with Axe-core as source, allow for counting incomplete, inapplicable, and passed rule checks, in addition to violations. Closes [2026](https://github.com/ICTU/quality-time/issues/2026).

### Removed

- Remove the 'random number' source. Closes [#2038](https://github.com/ICTU/quality-time/issues/2038).
- It's no longer possible to make *Quality-time* wait before sending a notification. Closes [#2039](https://github.com/ICTU/quality-time/issues/2039).

## v3.20.0 - 2021-04-07

### Fixed

- When a measurement detail, such as a violation or failed CI-job, is no longer reported by the source, remember its status (confirmed, false positive, won't fix, etc.) for three weeks so that if the detail reappears, its status is reapplied as well. Fixes [#1867](https://github.com/ICTU/quality-time/issues/1867).

### Added

- Reports can be exported and imported via API. Partially fixes [1693](https://github.com/ICTU/quality-time/issues/1693).
- When measuring security warnings with OWASP ZAP as source, allow for counting alert types as security warnings as opposed to alert instances. Closes [#1902](https://github.com/ICTU/quality-time/issues/1902).
- Added a new metric 'source version' that can be used to measure the version of a source and compare it with a minimum or maximum version number. See the [metrics and sources overview](metrics_and_sources.md) for a list of sources that support this metric. Closes [#1904](https://github.com/ICTU/quality-time/issues/1904).
- Added support for the Anchore Jenkins plugin as source for the 'security warnings' and 'source up-to-dateness' metrics. Closes [#1980](https://github.com/ICTU/quality-time/issues/1980).
- Added support for Axe-core JSON files (or zips with Axe-core JSON files) as source for measuring accessibility violations. Closes [#1981](https://github.com/ICTU/quality-time/issues/1981).

### Removed

- The axe-selenium-python source type has been removed. To read JSON files produced by axe-selenium-python, use the new Axe-core source type. This works, as the JSON format produced by axe-selenium-python is basically the same as the format produced by Axe-core. Sources of type axe-selenium-python in existing reports are automatically changed into Axe-core. No user action is needed.

## v3.19.1 - 2021-02-28

### Fixed

- The *Quality-time* API would return an internal server error (status code 500) if the database contains a source of a type that is no longer supported. Fixes [#1732](https://github.com/ICTU/quality-time/issues/1732).
- When opening *Quality-time*, don't show the user as logged in when their session has expired. Fixes [#1927](https://github.com/ICTU/quality-time/issues/1927).
- When measuring the up-to-dateness of a folder in GitLab with more than 100 files or subfolders, *Quality-time* uses the GitLab pagination API to retrieve the files and subfolders in batches of 100 each. However, due to a bug, the collector component would get stuck in a loop, retrieving the same files over and over again. Fixes [#1938](https://github.com/ICTU/quality-time/issues/1938).
- Notifier would not work for recently set notification destinations. Fixes [#1946](https://github.com/ICTU/quality-time/issues/1946).

## v3.19.0 - 2021-02-21

### Fixed

- When measuring size (lines of code) with SonarQube as source, some languages couldn't be ignored. Fixes [#1818](https://github.com/ICTU/quality-time/issues/1818).
- The trend table view would format durations incorrectly, e.g. 5 minutes would be displayed as '5 hours'. Fixes [#1900](https://github.com/ICTU/quality-time/issues/1900).
- Anchore security warnings have no hash. *Quality-time* would create a hash based on the security warning's CVE and affected package. However, if the Anchore source consists of a zip file with multiple reports, multiple combinations of the same CVE and package may be present. Add the report filename to the hash to make it unique. Fixes [#1907](https://github.com/ICTU/quality-time/issues/1907).
- When measuring security warnings with SonarQube as source, allow for filtering security hotspots by review priority. Fixes [#1910](https://github.com/ICTU/quality-time/issues/1910).
- The trend table view would sometimes, erroneously, show recent data as missing. Fixes [#1924](https://github.com/ICTU/quality-time/issues/1924).

### Added

- Add a 'merge requests' metric and add Azure Devops and GitLab as possible sources. Closes [#1644](https://github.com/ICTU/quality-time/issues/1644).

## v3.18.0 - 2021-02-03

### Fixed

- Prevent notifier crashes. Fixes [#1830](https://github.com/ICTU/quality-time/issues/1830) and [#1878](https://github.com/ICTU/quality-time/issues/1878).
- Logical sorting for entity status options. Fixes [#1841](https://github.com/ICTU/quality-time/issues/1841).

### Added

- Subjects can now show metrics in a trend table view. Use the hamburger menu to switch between the default detail view and the trend table view. Closes [#1649](https://github.com/ICTU/quality-time/issues/1649).
- When measuring failed pipelines or unused pipelines with Azure DevOps as source, allow for including pipelines by name or by regular expression. Prepares for [#1804](https://github.com/ICTU/quality-time/issues/1804).
- Allow using Azure DevOps pipelines as source for the 'source up-to-dateness' metric. Closes [#1804](https://github.com/ICTU/quality-time/issues/1804).

## v3.17.1 - 2021-01-24

### Fixed

- When measuring failed jobs with GitLab as source, *Quality-time* would get the 100 most recent jobs instead of the 100 most recent *failed* jobs. Fixes [#1813](https://github.com/ICTU/quality-time/issues/1813).
- Make sure the notifier component does not crash when a metric has no recent measurements. Fixes [#1831](https://github.com/ICTU/quality-time/issues/1831).
- Adding or removing the OWASP ZAP "Parts of URLs to ignore" parameter would fail. Fixes [#1846](https://github.com/ICTU/quality-time/issues/1846).

## v3.17.0 - 2021-01-17

### Changed

- Wrap the database (MongoDB), proxy (Caddy) and renderer (url-to-pdf-api) in *Quality-time* images, so these components have the same version number as the other components and don't need to be updated by downstream maintainers separately. Note that your Docker composition needs to be changed once to use these new *Quality-time* images. See the example [docker-compose.yml](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml). Closes [#1770](https://github.com/ICTU/quality-time/issues/1770).
- Increase render timeout so that larger reports can be exported to pdf. Closes [#1771](https://github.com/ICTU/quality-time/issues/1771).
- Add no-cache config for /api/v3/logo to the [Caddy config](https://github.com/ICTU/quality-time/blob/master/components/proxy/Caddyfile).

### Fixed

- The frontend would reload the change log every time the server notified the frontend about the number of measurements, causing unnecessary updates of the UI. Fixes [#1555](https://github.com/ICTU/quality-time/issues/1555).
- When the user opens a report in the frontend, don't send unneeded data to the frontend. Fixes [#1764](https://github.com/ICTU/quality-time/issues/1764).
- Don't crash the notifier when a metric has an unknown (white) status. Fixes [#1802](https://github.com/ICTU/quality-time/issues/1802).
- Some dependencies in the OWASP Dependency Check report have no hash. In those cases *Quality-time* would create a hash based on the file path of the dependency. However, file paths aren't necessarily unique across dependencies. Add the file name to the hash to make it unique. Fixes [#1819](https://github.com/ICTU/quality-time/issues/1819).

### Added

- Add the tags of accessibility rules to the detail information of axe-selenium-python sources. Closes [#1751](https://github.com/ICTU/quality-time/issues/1751).
- Allow for filtering axe-selenium-python accessibility violations by tag. Closes [#1752](https://github.com/ICTU/quality-time/issues/1752).

## v3.16.0 - 2020-12-12

### Added

- Show since when a metric has its current status via a popup over the status icon. Closes [#1091](https://github.com/ICTU/quality-time/issues/1091).
- When adding a notification destination, it's possible to specify how long *Quality-time* should wait before sending a notification. If more notifications happen during the wait period, they will be bundled. Also see the [user manual](usage.md#notifications). Partially implements [#1223](https://github.com/ICTU/quality-time/issues/1223).
- Notifications will now be sent for all status changes. Previously, notifications were only sent when a metric either turned red or white. Partially implements [#1223](https://github.com/ICTU/quality-time/issues/1223).
- Allow using Jenkins jobs as source for the 'source up-to-dateness' metric. Closes [#1680](https://github.com/ICTU/quality-time/issues/1680).

### Fixed

- Accepting the technical debt of a metric with one or more unreachable sources would set the metric status to 'technical debt target met' instead of 'unknown'. Fixes [#1636](https://github.com/ICTU/quality-time/issues/1636).
- Collapsing an expanded metric would sometimes result in a crash of the frontend. Fixes [#1717](https://github.com/ICTU/quality-time/issues/1717).

### Changed

- MongoDB was upgraded to 4.2.11. No migration steps are needed. Simply update the MongoDB version number in your composition configuration.

## v3.15.0 - 2020-11-29

### Added

- When using Jira as source for the 'issues' and the 'user story points' metric, show the issue type in the metric details. Closes [#1674](https://github.com/ICTU/quality-time/issues/1674).
- Allow for limiting editing rights to specific people. Grant editing rights to people by adding their username or email address to the editors field on the homepage. Expand the overview title to access the editors field. Also see the [user manual](usage.md#configuring-permissions). Closes [#294](https://github.com/ICTU/quality-time/issues/294).

### Fixed

- When invoking the reports API endpoint (api/v3/reports) without a `report_date` parameter, the server would sometimes return a deleted report. Fixes [#1683](https://github.com/ICTU/quality-time/issues/1683).
- Make sure that the collector does not crash when a metric has a source that is no longer supported. Fixes [#1699](https://github.com/ICTU/quality-time/issues/1699).
- When measuring test branch coverage with a JaCoCo XML file that doesn't contain any branches, don't complain but simply report 100% coverage. Fixes [#1700](https://github.com/ICTU/quality-time/issues/1700).

## v3.14.1 - 2020-11-17

### Fixed

- Undo the fix for [#1656](https://github.com/ICTU/quality-time/issues/1656) as it causes timeouts. This fix was meant to prevent 403 responses (access forbidden) from GitLab when using HEAD requests. If they do still happen (can't reproduce at the moment) we'll need to find another solution. Fixes [#1675](https://github.com/ICTU/quality-time/issues/1675).
- Turn on processing of all DTD's (despite the fact that security tools complain that this is insecure) because otherwise XML reports referring to a DTD can't be read. Fixes [#1676](https://github.com/ICTU/quality-time/issues/1676).

## v3.14.0 - 2020-11-15

### Added

- When hiding the tags column, also hide the tag pie charts in the report dashboard. Closes [#1595](https://github.com/ICTU/quality-time/issues/1595).
- Allow for adding more than one Microsoft Teams webhook to a report so notifications can be sent to more than one channel.

### Changed

- Group Snyk security warnings by top-level dependency. Closes [#1616](https://github.com/ICTU/quality-time/issues/1616). Contributed by [@greckko](https://github.com/greckko).

### Removed

- Remove support for the source "OWASP Dependency Check Jenkins plugin". Fixes [#1666](https://github.com/ICTU/quality-time/issues/1666).

### Fixed

- In Microsoft Teams notifications, show missing values as "?" rather than "None". Fixes [#1637](https://github.com/ICTU/quality-time/issues/1637).
- Turn on processing of DTD's (despite the fact that security tools complain that this is insecure) because otherwise some XML reports (notably OJAudit) can't be read. Fixes [#1655](https://github.com/ICTU/quality-time/issues/1655).
- When using folders and/or files in GitLab as source for the 'source up-to-dateness' metric, *Quality-time* would use HEAD requests to get the ids of commits from GitLab. For issue [#1638](https://github.com/ICTU/quality-time/issues/1638), it was necessary to pass the private token as header instead of URL parameter. Unfortunately, this results in 403 (access forbidden) responses for HEAD requests. It's unclear why. Using GET requests instead does work, so we use that as a work-around. Fixes [#1656](https://github.com/ICTU/quality-time/issues/1656).

## v3.13.0 - 2020-11-08

### Added

- When using the Performancetest-runner as source for the 'slow transactions' or 'tests' metric, add a transactions-to-include parameter in addition to the transactions-to-ignore parameter to make it easier to select the relevant transactions. Closes [#1647](https://github.com/ICTU/quality-time/issues/1647).

### Removed

- The SonarQube rules that *Quality-time* uses to query SonarQube for the 'commented out code', 'complex units', 'long units', 'many parameters', and 'suppressed violations' metrics are no longer a parameter that the user can change. The reason is that it's hardly ever necessary to change these parameters and at the same time it's very easy to accidentally remove a rule and get incorrect results as a consequence. The used rules are documented in the [metrics and sources overview](metrics_and_sources.md). Closes [#1648](https://github.com/ICTU/quality-time/issues/1648).

### Changed

- When using GitLab as source with a private token, pass the token to GitLab as header instead of URL parameter to prevent redirection. Closes [#1638](https://github.com/ICTU/quality-time/issues/1638).

### Fixed

- Introduce separate namespace for internal API's. Fixes [#1632](https://github.com/ICTU/quality-time/issues/1632).
- When using the same Microsoft Teams webhook in multiple reports, notifications for one report could also contain metrics of other reports.

## v3.12.0 - 2020-10-31

### Added

- When a report has a Microsoft Teams webhook configured, in addition to sending notifications for metrics turned red (target not met), also send notifications when metrics turn white (error parsing source data or troubles connecting to source). Partially implements [#1223](https://github.com/ICTU/quality-time/issues/1223).
- Add a trend table to each metric to see the trend of a metric in tabular form. The number of dates shown and the time between dates can be adjusted through the 'hamburger' menu in the table header. Closes [#1536](https://github.com/ICTU/quality-time/issues/1536).
- When measuring with SonarQube as source, include the creation date and last update date of issues such as violations and security warnings in the metric details. Closes [#1564](https://github.com/ICTU/quality-time/issues/1564).
- In addition to ignoring Jenkins jobs by name or regular expression, also allow for including Jenkins jobs by name or regular expression. Closes [#1596](https://github.com/ICTU/quality-time/issues/1596).

### Fixed

- When a source zip file doesn't contain any files with the expected extension, report an error instead of continuing with an empty list of files, because that may result in incorrect measurements. Fixes [#1618](https://github.com/ICTU/quality-time/issues/1618).

## v3.11.0 - 2020-10-25

### Added

- Added a generic JSON file format that can be used as source for the 'security warnings' metric. See the [user manual](usage.md#generic-json-format-for-security-warnings) for details on the exact format. Closes [#1479](https://github.com/ICTU/quality-time/issues/1479). Contributed by [@greckko](https://github.com/greckko).
- Include the expanded/collapsed state of metrics, including which tab is active, in the URL so that the renderer uses that state when exporting the report to PDF. Closes [#1594](https://github.com/ICTU/quality-time/issues/1594).
- In the Microsoft Teams notifications, include which metric(s) turned red. Partially implements [#1223](https://github.com/ICTU/quality-time/issues/1223).

## v3.10.0 - 2020-10-18

### Added

- Support for Forwarded Authentication in a situation where *Quality-time* is behind a reverse proxy that is responsible for authentication. See the [deployment instructions](deployment.md#configuring-forwarded-authentication).
- Notifications of new red metrics to Microsoft Teams, using webhooks. See the [user manual](usage.md#notifications). Note that your Docker composition needs to be changed to include the new notifier component. See the example [docker-compose.yml](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml) and the [deployment instructions](deployment.md#notifier). Partially implements [#1223](https://github.com/ICTU/quality-time/issues/1223).

## v3.9.0 - 2020-10-11

### Added

- When measuring 'tests' with the Performancetest-runner as source, allow for ignoring transactions by name or regular expression. Closes [#1550](https://github.com/ICTU/quality-time/issues/1550).

### Fixed

- Show how to set the time zone of the renderer in the [docker-compose.yml](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml) so that PDF exports contain the correct local time. Fixes [#1529](https://github.com/ICTU/quality-time/issues/1529).
- The date picker for the end date of technical debt has a minimum date set to today. Apparently, if the current value of the technical debt end date is far enough in the past so that the whole month popup consists of disabled dates, the date picker will crash. Worked around by removing the minimum date. Fixes [#1534](https://github.com/ICTU/quality-time/issues/1534).
- Running `docker-compose up` in the project root folder wouldn't work on Windows. Fixes [#1543](https://github.com/ICTU/quality-time/issues/1543).

## v3.8.0 - 2020-10-04

### Changed

- Use local time instead of UTC in the filenames of PDF exports. Closes [#1505](https://github.com/ICTU/quality-time/issues/1505).

### Added

- The 'slow transactions' metric with the Performancetest-runner as source allows for ignoring transactions by name or by regular expression. Closes [#1493](https://github.com/ICTU/quality-time/issues/1493).
- The 'tests' metric now also supports the percentage scale so it's possible to e.g. report the percentage of tests failed. Closes [#1494](https://github.com/ICTU/quality-time/issues/1494).
- Added Cobertura Jenkins plugin as possible source for the 'test line coverage', 'test branch coverage', and 'source up-to-dateness' metrics. Closes [#1520](https://github.com/ICTU/quality-time/issues/1520).
- Added Robot Framework Jenkins plugin as possible source for the 'tests', and 'source up-to-dateness' metrics. Closes [#1521](https://github.com/ICTU/quality-time/issues/1521).

### Fixed

- Some exceptions thrown by the aiohttp library have no explicit error message. This would cause *Quality-time* to try and parse the non-existing source response, erroneously complaining about a parse error. Although in these cases the connection error would be logged, without an error message the logging would not be very informative. Fixed by having the collector log the class of the aiohttp exception if the error message is empty. Fixes [#1422](https://github.com/ICTU/quality-time/issues/1422).
- The PDF export would always export the most recent report, even when the user picked another date. Fixes [#1498](https://github.com/ICTU/quality-time/issues/1498).
- The 'commented-out code' metric claimed to measure the number of lines of commented-out code, but SonarQube actually reports the number of *blocks* of commented-out lines of code. Changed the metric description and unit to conform to the SonarQube data. Fixes [#1507](https://github.com/ICTU/quality-time/issues/1507).
- Trend graphs showing metrics with minutes as unit would have their y-axis labeled 'hours'. Fixes [#1522](https://github.com/ICTU/quality-time/issues/1522).
- Tokens with an underscore would not be completely redacted from the collector log. Fixes [#1523](https://github.com/ICTU/quality-time/issues/1523).

## v3.7.0 - 2020-09-27

### Added

- When exporting quality reports to PDF, hide the same metric table rows and columns in the PDF as hidden by the user in the user interface. Closes [#1466](https://github.com/ICTU/quality-time/issues/1466).
- In addition to the trend, target, source, comment, and tags columns, also allow for hiding the status and measurement columns in metric tables. Closes [#1474](https://github.com/ICTU/quality-time/issues/1474).

### Fixed

- The measurement value and target of metrics with unit minutes and their scale set to percentage were formatted incorrectly (e.g. "0:50%" instead of "50%"). Fixes [#1480](https://github.com/ICTU/quality-time/issues/1480).
- The measurement value and target of metrics with unit minutes and their scale set to count were displayed as '`hours`:`minutes` minutes'. This would be confusing: e.g. '3:10 minutes' looks like 3 minutes and 10 seconds instead of 3 hours and 10 minutes. Fixed by changing 'minutes' to 'hours'. Fixes [#1484](https://github.com/ICTU/quality-time/issues/1484).
- The security warnings in OWASP ZAP reports do not have unique keys. However, *Quality-time* needs security warnings to be uniquely identifiable to detect whether the list of warnings changes between measurements. Therefore, *Quality-time* generates keys for OWASP ZAP security warnings itself. Unfortunately, the key that *Quality-time* generated, was not guaranteed to be unique. Fixes [#1492](https://github.com/ICTU/quality-time/issues/1492).
- Time travel was broken. Fixes [#1497](https://github.com/ICTU/quality-time/issues/1497).

## v3.6.0 - 2020-09-19

### Changed

- Moved the button to hide metrics that don't require action to the new 'hamburger' menu on the top left side of each metric table. The menu is needed to allow for menu items to hide columns. See [#1464](https://github.com/ICTU/quality-time/issues/1464).

### Added

- Support version 2.4 and 2.5 of the OWASP Dependency Check XSD. Closes [#1460](https://github.com/ICTU/quality-time/issues/1460).
- Allow for hiding the trend, target, source, comment, and tags columns in the metric tables. This can be done through the 'hamburger' menu on the top left side of each metric table. Closes [#1464](https://github.com/ICTU/quality-time/issues/1464).

### Fixed

- Retrieving measurements for the trend graph of a metric with many measurements and details (violations, user stories, security warnings, etc.) was slow because *Quality-time* would retrieve all details for all measurements even though it only needs the details for the most recent measurement. Fixes [#1468](https://github.com/ICTU/quality-time/issues/1468).

## v3.5.0 - 2020-09-12

### Fixed

- Open source detail URLs (e.g. links to individual user stories or violations) in a separate window or tab. Fixes [#1434](https://github.com/ICTU/quality-time/issues/1434).
- When measuring 'velocity' with Jira as source, *Quality-time* would only retrieve the first 50 boards from Jira, making the metric fail for some boards. Fixes [#1445](https://github.com/ICTU/quality-time/issues/1445).

### Changed

- Right align columns with numbers in the metric details. Closes [#1384](https://github.com/ICTU/quality-time/issues/1384).

### Added

- Added TestNG XML reports as possible source for the 'tests' and 'source up-to-dateness' metrics. Closes [#1204](https://github.com/ICTU/quality-time/issues/1204).
- When measuring 'velocity' with Jira as source, the metric can also report the number of points committed to. Closes [#1406](https://github.com/ICTU/quality-time/issues/1406).
- When measuring 'velocity' with Jira as source, the metric can also report the number of points completed minus the number of points committed to. Closes [#1408](https://github.com/ICTU/quality-time/issues/1408).

## v3.4.0 - 2020-09-05

### Fixed

- Use the default value of a source parameter if the user sets it to an empty string. Fixes [#1417](https://github.com/ICTU/quality-time/issues/1417).
- SonarQube plugins for Java and JavaScript had some of their rules renamed. Add the renamed rules to the 'commented out code', 'complex units', 'many parameters', 'long units', and 'suppressed violations' metrics. Fixes [#1423](https://github.com/ICTU/quality-time/issues/1423).

### Changed

- Rename the 'ready user story points' to 'user story points' as it can not just be used to count ready user stories, but rather any selection of user stories. Closes [#1415](https://github.com/ICTU/quality-time/issues/1415).

### Added

- Add 'velocity' metric. Currently, the only source supported for this metric is Jira. Closes [#1407](https://github.com/ICTU/quality-time/issues/1407).
- Add [axe-selenium-python](https://github.com/mozilla-services/axe-selenium-python) JSON reports as possible source for the 'accessibility violations' metric. Closes [#1424](https://github.com/ICTU/quality-time/issues/1424).

## v3.3.0 - 2020-08-29

### Fixed

- The 'source up-to-dateness' metric combined with the Calendar would report a parse error instead of returning the number of days since the specified date. Fixes [#1399](https://github.com/ICTU/quality-time/issues/1399).
- After an attempt to login with invalid credentials and closing/reopening the login dialog, it would still show the error message. Fixes [#1401](https://github.com/ICTU/quality-time/issues/1401).
- When measuring 'tests' with Azure Devops, test runs could not be marked as false positive or won't fix. Fixes [#1402](https://github.com/ICTU/quality-time/issues/1402).
- Specifying the Jira user story point field only worked if done by id, not by name. Fixes [#1409](https://github.com/ICTU/quality-time/issues/1409).

### Added

- When measuring ready user story points with Jira as source, show the sprint(s) of the user stories in the details. When measuring issues with Jira as source, show issue status, priority, sprint(s), creation date, and date of last update in the details. Closes [#1411](https://github.com/ICTU/quality-time/issues/1411).

## v3.2.0 - 2020-08-22

### Fixed

- When measuring the 'manual test duration' metric *Quality-time* would subtract one minute for each ignored test case, instead of the duration of the ignored test case. Fixes [#1361](https://github.com/ICTU/quality-time/issues/1361).
- *Quality-time* would not measure the 'manual test execution' metric until the user changed the 'default expected manual test execution frequency' field. Fixes [#1363](https://github.com/ICTU/quality-time/issues/1363).
- SonarQube doesn't consider security hotspots to be violations anymore since version 8.2. Therefore, when using SonarQube as source for the 'violations' or the 'suppressed violations' metric, you can no longer select security hotspots as a violation type to be included or excluded. If you have a 'violations' or 'suppressed violations' metric that was configured to measure only the number of security hotspots you will need to remove it, as it will now measure all violation types. To count security hotspots, use the 'security warnings' metric with SonarQube as source instead, and configure it to only count security hotspots. Fixes [#1381](https://github.com/ICTU/quality-time/issues/1381).
- When measuring 'tests' with Azure DevOps, only the latest build of all matching test runs was reported instead of the latest build of each matching test run. Fixes [#1382](https://github.com/ICTU/quality-time/issues/1382).
- Jenkins jobs with slashes in their names couldn't be marked as false positive or won't fix. Fixes [#1390](https://github.com/ICTU/quality-time/issues/1390).
- Typing an invalid date in the report date picker would crash the front end. Fixes [#1394](https://github.com/ICTU/quality-time/issues/1394).

### Added

- When measuring the number of test cases using Jenkins test report as source, for each failing test case show for how many builds it has been failing. Closes [#1373](https://github.com/ICTU/quality-time/issues/1373).
- Add a new metric 'violation remediation effort' that reports the effort needed to remediate violations. Currently, the only source supporting this metric is SonarQube. Closes [#1374](https://github.com/ICTU/quality-time/issues/1374).
- Allow for filtering Azure DevOps test runs by test run state. Closes [#1383](https://github.com/ICTU/quality-time/issues/1383).
- Added Snyk JSON reports as source for the 'security warnings' metric. Contributed by [@greckko](https://github.com/greckko).

## v3.1.0 - 2020-08-07

### Fixed

- Trend graph didn't take technical debt end date into account. Fixes [#1272](https://github.com/ICTU/quality-time/issues/1272).
- Don't store the age of last commits, last builds, and last execution of manual tests, but only the date. This prevents the measurements from being updated daily. Fixes [#1341](https://github.com/ICTU/quality-time/issues/1341).
- Don't show tokens in the log of the collector when retrieving the URL fails. Fixes [#1354](https://github.com/ICTU/quality-time/issues/1354).

### Added

- When measuring the 'size' metric with SonarQube, show the non-commented lines of code per programming language as measurement details and allow for ignoring specific languages. Due to a SonarQube limitation this is only possible when measuring size using non-commented lines of code (the default) and not when measuring size using all lines. Closes [#1216](https://github.com/ICTU/quality-time/issues/1216).
- When measuring 'issues' with Jira, show status, priority, creation date and last update date for each issue in the details tab. Closes [#1351](https://github.com/ICTU/quality-time/issues/1351).

### Changed

- Increase the number of ticks on the x-axis of trend graphs. Closes [#1126](https://github.com/ICTU/quality-time/issues/1126).

## v3.0.0 - 2020-07-31

### Fixed

- When opening a tag report containing a subject without a name, the UI would complain that the server is unavailable. Fixes [#1309](https://github.com/ICTU/quality-time/issues/1309).
- Parse JSON files even if the source web server doesn't set the content-type header to application/json. Fixes [#1325](https://github.com/ICTU/quality-time/issues/1325). Contributed by [@walterdeboer](https://github.com/walterdeboer).

### Added

- When using GitLab as source for the 'unused jobs' or 'failed jobs' metrics, allow for ignoring jobs/pipelines by name, by branch, and by tag. Closes [#1288](https://github.com/ICTU/quality-time/issues/1288).

### Changed

- *Quality-time* now uses version 3 of the *Quality-time* API to read data from other *Quality-time* instances for the 'metrics' metric. This means that the source-*Quality-time* needs to be at least version 2.4.0. Closes [#1208](https://github.com/ICTU/quality-time/issues/1208).
- Upgrade Python to version 3.8.5. Closes [#1314](https://github.com/ICTU/quality-time/issues/1314).

### Removed

- Version 2 of the *Quality-time* API, which was deprecated since version 2.4.0, has been removed.
- Remove code to fix the database structure. If you are migrating from a *Quality-time* version < 2.0.0 you need to install at least one *Quality-time* version >= 2.0.0 and < 3.0.0.

## v2.5.2 - 2020-07-10

### Fixed

- Removing the end date of accepted technical debt would not correctly update the metric status. Fixes [#1284](https://github.com/ICTU/quality-time/issues/1284).
- The 'tests' metric with the Performancetest-runner as source would fail to read the number of performance tests due to changes in the report format. Fixes [#1291](https://github.com/ICTU/quality-time/issues/1291).

## v2.5.1 - 2020-07-06

### Fixed

- Older GitLab versions don't return a `web_url` as part of the `repository/branches` API, be prepared. Fixes [#1280](https://github.com/ICTU/quality-time/issues/1280).

## v2.5.0 - 2020-07-05

### Fixed

- Sorting the unmerged branches by date of last commit would crash the UI. Fixes [#1270](https://github.com/ICTU/quality-time/issues/1270).

### Added

- *Quality-time* can be used as source for the 'source up-to-dateness' metric. Closes [#1227](https://github.com/ICTU/quality-time/issues/1227).
- Have unmerged branches in *Quality-time* link to the branches in GitLab or Azure DevOps. Closes [#1268](https://github.com/ICTU/quality-time/issues/1268).
- Documentation on how to add metrics and sources to *Quality-time*. Closes [#1273](https://github.com/ICTU/quality-time/issues/1273).
- Add Cobertura coverage reports as source for the coverage metrics. Closes [#1275](https://github.com/ICTU/quality-time/issues/1275).

## v2.4.1 - 2020-06-25

### Fixed

- Don't disable the 'scroll to dashboard' button when the dashboard is visible. This requires listening for scroll events which makes scrolling of big reports slow and causes other user interface issues like dropdown menu's not working. Fixes [#1260](https://github.com/ICTU/quality-time/issues/1260) and [#1261](https://github.com/ICTU/quality-time/issues/1261).

## v2.4.0 - 2020-06-23

### Added

- Add [cloc](https://github.com/AlDanial/cloc) as source for the 'size' metric. As opposed to SonarQube, cloc makes it easy to exclude certain programming languages from the size measurement. Closes [#460](https://github.com/ICTU/quality-time/issues/460).
- When using Azure DevOps as source for the 'tests' metric, allow for filtering tests by test run name and show the test runs as detail information. Closes [#1215](https://github.com/ICTU/quality-time/issues/1215).
- Add a button to the menu bar to scroll to the dashboard. Closes [#1231](https://github.com/ICTU/quality-time/issues/1231).
- Add OWASP Dependency Check as source for the 'dependencies' metric. Closes [#1239](https://github.com/ICTU/quality-time/issues/1239).

### Changed

- Moved the Copy and Move buttons next to the Add buttons, making the UI more consistent. This also allows the user to copy an existing item to the right position in one go, instead of having to copy and then move it. To support adding items by copying an existing item, the API has been updated to version 3. Version 2 of the API is deprecated. See <http://quality-time.example.org/api/>, <http://quality-time.example.org/api/v2>, and <http://quality-time.example.org/api/v3>. Note that your Docker composition may need to be changed to use the new API version. See the Caddy proxy configuration in the example [docker-compose.yml](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml). Closes [#1197](https://github.com/ICTU/quality-time/issues/1197).

### Fixed

- Reordering items or changing the type of a metric would sometimes fail because *Quality-time* would also try to save the layout of the dashboard. Fixed by only saving the dashboard layout when the user deliberately changes the layout by dragging a card. Fixes [#1160](https://github.com/ICTU/quality-time/issues/1160).
- Columns with numbers in the source entity views were incorrectly sorted as text. Fixes [#1196](https://github.com/ICTU/quality-time/issues/1196).
- Collecting unmerged branches using Azure DevOps as source would fail if the project name contained spaces and the user did not specify a repository. *Quality-time* would fail to find the default repository because it would use the URL-quoted project name to look for it, instead of the unquoted project name. Fixes [#1224](https://github.com/ICTU/quality-time/issues/1224).
- When using Jira as source for the 'ready user story points' metric, changing the status of a user story in the details tab didn't work. Fixes [#1230](https://github.com/ICTU/quality-time/issues/1230).
- When using Jira as source for the 'ready user story points' metric, changing the status of a user story in the details tab to won't fix, false positive or fixed would reduce the total number of story points with one instead of the number of story points of the ignored user story. Fixes [#1233](https://github.com/ICTU/quality-time/issues/1233).
- The `git clone` URL in the [README.md](https://github.com/ICTU/quality-time/blob/master/README.md) required people to have a public SSH key added to their GitHub account. Replaced with a https URL which doesn't have this issue. Fixes [#1235](https://github.com/ICTU/quality-time/issues/1235).
- When using the OWASP Dependency Check as source for the 'security warnings' metric, changing the status of a warning in the details tab didn't work. Fixes [#1238](https://github.com/ICTU/quality-time/issues/1238).
- The trend sparkline graphs, showing the trend over the last week, would always use the full width, even when there was less than a week of data. Fixes [#1241](https://github.com/ICTU/quality-time/issues/1241).

## v2.3.2 - 2020-06-10

### Changed

- Open the source links in separate window. Closes [#1203](https://github.com/ICTU/quality-time/issues/1203).

### Fixed

- The 'source up-to-dateness' metric could report a negative number of days ago due to differences in timezone or system clock between *Quality-time* and the source. Fixes [#1217](https://github.com/ICTU/quality-time/issues/1213).
- Re-enable environment variables to set a proxy to be used by the collector. See the [deployment documentation](deployment.md). Fixes [#1217](https://github.com/ICTU/quality-time/issues/1217).

## v2.3.1 - 2020-06-02

### Fixed

- Don't strip hyphens from usernames when authenticating them with LDAP. Fixes [#1198](https://github.com/ICTU/quality-time/issues/1198).

## v2.3.0 - 2020-06-01

### Added

- SonarQube can be used as source for the 'security warnings' metric. *Quality-time* collects the vulnerabilities and/or security hotspots. Closes [#1136](https://github.com/ICTU/quality-time/issues/1136).
- npm-outdated and pip-outdated JSON reports can be used as source for the 'dependencies' metric. Partially implements [#1065](https://github.com/ICTU/quality-time/issues/1065).

### Fixed

- *Quality-time* was using the 5.1 version of the Azure DevOps API to get the number of tests for the 'tests' metric causing *Quality-time* to not work with Azure DevOps Server 2019. Fixed by using the 5.0 version of the API that also returns the required data. Fixes [#1182](https://github.com/ICTU/quality-time/issues/1182).
- Don't log a traceback the first time the collector component attempts to download the data model from the server component and fails. As the collector typically starts up faster than the server, one failed attempt is to be expected. Fixes [#1187](https://github.com/ICTU/quality-time/issues/1187).

## v2.2.4 - 2020-05-11

### Fixed

- Adding a metric or changing the type of a metric would sometimes fail due to a conflict with saving the dashboard layout. Fixed by only saving the dashboard layout when the user manually rearranges cards and not when a card gets added or removed. Fixes [#1160](https://github.com/ICTU/quality-time/issues/1160).

## v2.2.3 - 2020-05-10

### Fixed

- When using *Quality-time* as source for the Metrics metric, a timeout could occur due to *Quality-time* unnecessarily retrieving all measurements (it only needs the most recent ones). Fixes [#1154](https://github.com/ICTU/quality-time/issues/1154).

## v2.2.2 - 2020-04-22

### Fixed

- Don't include SonarQube security hotspots in the complex units, long units, many parameters, commented out code, and suppressed violations metrics. Fixes [#1138](https://github.com/ICTU/quality-time/issues/1138) introduced in v2.2.1.

## v2.2.1 - 2020-04-22

### Fixed

- [When requesting issues with a severity from SonarQube, SonarQube will not return security hotspots because security hotspots don't have a severity](https://community.sonarsource.com/t/issues-api-does-not-return-security-hotspots-when-passing-a-severity/23326). *Quality-time* incorrectly assumed security hotspots would always be returned regardless of the specified severities. Fixed by making a separate call to the SonarQube issues API if necessary to retrieve the security hotspots. Fixes [#1135](https://github.com/ICTU/quality-time/issues/1135).

## v2.2.0 - 2020-04-14

### Added

- Trend graphs show the target, near target, and technical debt target (if technical debt is accepted) as background colors. Note that the background colors only become visible after the measurement value of a metric changes or one of its target values is edited. Closes [#1087](https://github.com/ICTU/quality-time/issues/1087).

### Changed

- Make it clear in the user interface and the documentation that *Quality-time* can be authenticated with Jenkins using a username and API token, in addition to a username and password. Closes [#1125](https://github.com/ICTU/quality-time/issues/1125).

### Fixed

- Remove private tokens from source error messages and collector logging. Fixes [#1127](https://github.com/ICTU/quality-time/issues/1127).

## v2.1.1 - 2020-04-03

### Fixed

- When the collector fails to collect a measurement, a traceback would be included in the measurement. Unfortunately, tracebacks with the new asynchronous collector are very long. To prevent performance issues, the collector now only logs the error in the case of connection errors. Other types of errors still include a traceback. Fixes [#1122](https://github.com/ICTU/quality-time/issues/1122).

## v2.1.0 - 2020-03-29

### Changed

- The collector wakes up every minute, collects measurement data if necessary, and then would pause for a minute. Changed to have the length of the pause depend on how long the data collection took so that the user does not have to wait too long for a new measurement after changing the configuration of a metric. Closes [#1100](https://github.com/ICTU/quality-time/issues/1100).
- Made the collector collect measurements in parallel to speed it up.

### Fixed

- The metrics "violations" and "suppressed violations" show zero violations (green status) even though the component has no SonarQube analysis. Fixes [#1090](https://github.com/ICTU/quality-time/issues/1090).

## v2.0.0 - 2020-03-08

### Added

- Add a private token parameter to all sources that consists of JSON, XML, or HTML reports so that they can be retrieved from GitLab job artifacts. Closes [#1067](https://github.com/ICTU/quality-time/issues/1067).
- Add a column to show the status (unconfirmed, confirmed, false positive, etc.) of security warnings, violations, etc. so that the user doesn't have to expand them to see the status. Closes [#1070](https://github.com/ICTU/quality-time/issues/1070).
- Show end date of technical debt in the measurement target column. Closes [#1072](https://github.com/ICTU/quality-time/issues/1072).
- Allow for accepting technical debt for a metric that has no sources or failing sources. Closes [#1076](https://github.com/ICTU/quality-time/issues/1076).
- Make date fields clearable. Closes [#1088](https://github.com/ICTU/quality-time/issues/1088).

### Fixed

- Don't store server-side generated report summaries in the database. The previously generated report summaries are removed from the database when the server starts, so starting may take longer than normal. Fixes [#1082](https://github.com/ICTU/quality-time/issues/1082).

### Removed

- Version 1 of the API has been removed. API version 1 was deprecated since *Quality-time* v1.3.0. Closes [#1051](https://github.com/ICTU/quality-time/issues/1051).
- Remove the Docker environment files and move the environment variables to the docker-compose files to simplify the compositions. Closes [#1063](https://github.com/ICTU/quality-time/issues/1063).

## v1.8.1 - 2020-03-03

### Fixed

- When loading changes to show in the changelog, an internal server error could occur due to Mongo hitting its maximum buffer size for sorting. Add an index to the reports collection to prevent out of memory errors during sorting. Fixes [#1077](https://github.com/ICTU/quality-time/issues/1077).

## v1.8.0 - 2020-03-01

### Changed

- Cache data model and other performance improvements. Note: the proxy settings for the data model API have been updated. See the Caddy configuration in the [docker-compose.yml](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.yml). The order of the metric tabs has been changed. From left to right: first tab is the metric configuration, second the source(s) configuration, third the trend graph, and finally the tab(s) with details per source, if applicable. This makes it possible to lazily load the data for the trend graph and the details per source and show the tabs as soon as the data becomes available. Fixes [#1026](https://github.com/ICTU/quality-time/issues/1026).

### Added

- Allow for specifying variable parts of URLs in OWASP ZAP reports. This makes it possible to mark warnings as false positive even when parts of URLs change between runs of OWASP ZAP. Note: because the way *Quality-time* keeps track of the warnings has been changed, some OWASP ZAP warnings may need to be marked as false positive again. Closes [#1045](https://github.com/ICTU/quality-time/issues/1045).
- A new metric for measuring the number of (outdated) dependencies and a new source (Composer for PHP) that supports this metric were added. Closes [#1056](https://github.com/ICTU/quality-time/issues/1056).

## v1.7.1 - 2020-02-26

### Fixed

- When using SonarQube as source for duplication, uncovered lines, or uncovered branches, the landing url would be incorrect. Fixes [#1044](https://github.com/ICTU/quality-time/issues/1044).
- The docker-compose YAML file now specifies that the proxy container should wait for the server and frontend containers to start. Fixes [#1046](https://github.com/ICTU/quality-time/issues/1046).
- The collector would fail if it could not write a timestamp to the health_check.txt file, e.g. due to a permission error. Fixed by writing the health_check.txt file to /tmp instead of the home directory of the default user and by catching and logging any OS errors that may occur. Fixes [#1057](https://github.com/ICTU/quality-time/issues/1057).

## v1.7.0 - 2020-02-22

### Changed

- As the previous rendering component used by *Quality-time* is no longer maintained, it is replaced with a new component: [URL to PDF Microservice](https://github.com/alvarcarto/url-to-pdf-api). *Quality-time* uses the [ICTU fork](https://github.com/ICTU/url-to-pdf-api) that packages the service as a [Docker container](https://hub.docker.com/repository/docker/ictu/url-to-pdf-api).

### Fixed

- The new rendering component (see "Changed") shows the date in the correct format. Fixes [#1010](https://github.com/ICTU/quality-time/issues/1010).
- Show tags added by users in the tag dropdown so they don't have to keep typing added tags. Fixes [#1041](https://github.com/ICTU/quality-time/issues/1041).

### Removed

- Because the new rendering component (see "Changed") waits for network activity to stop before converting a report into PDF, the delay parameter is no longer needed.

## v1.6.2 - 2020-02-19

### Fixed

- Use environment variables for both proxy host and port so the renderer uses the right URL to get the report. Fixes [#1031](https://github.com/ICTU/quality-time/issues/1031).
- OWASP ZAP warning keys were not always unique, causing trouble with marking them as false positive. Fixes [#1032](https://github.com/ICTU/quality-time/issues/1032).
- The Jenkins test report source would not correctly get the number of passed tests from aggregated test reports. Fixes [#1033](https://github.com/ICTU/quality-time/issues/1033).

## v1.6.1 - 2020-02-18

### Fixed

- Don't refresh the change log when clicking the "Download report as pdf" button. Fixes [#1015](https://github.com/ICTU/quality-time/issues/1015).
- Make proxy port configurable. Fixes [#1018](https://github.com/ICTU/quality-time/issues/1018).
- Changes made to violations, issues, warnings, etc., such as marking them as false positive, were only visible in the metric change log and not in the change logs of the report, subject, and source. Note: because a change needed to be made to the database format to fix this, changes made to violations, issues, warnings, etc. before this release are not visible in the change log. Fixes [#1019](https://github.com/ICTU/quality-time/issues/1019).
- Anchore vulnerability keys are not always valid as JSON key, causing exceptions when the user tries to make changes to vulnerabilities. Hashing the keys prevents this issue. Fixes [#1023](https://github.com/ICTU/quality-time/issues/1023).
- The too many parameters, complex units, and long unit metrics with SonarQube as source would always report the percentage as zero. Fixes [#1027](https://github.com/ICTU/quality-time/issues/1027).

## v1.6.0 - 2020-02-12

### Changed

- Several accessibility related changes, such as improved background colors, larger icons, more contrast, and labels for images. Closes [#1005](https://github.com/ICTU/quality-time/issues/1005).

### Fixed

- Changes made to violations, issues, warnings, etc., such as marking them as false positive, would not carry over after a failed measurement, forcing the user to make the same changes again. Fixes [#1007](https://github.com/ICTU/quality-time/issues/1007).

## v1.5.0 - 2020-02-09

### Added

- Jenkins jobs with the JaCoCo Jenkins plugin can be used as source for the line and branch coverage metrics. Closes [#984](https://github.com/ICTU/quality-time/issues/984).
- Add Anchore Docker image vulnerability scan reports in JSON format as possible source for the security warnings metric. Closes [#1000](https://github.com/ICTU/quality-time/issues/1000).

### Changed

- Center the status column so that the trend graphs and the status icons have a bit more space between them. Closes [#985](https://github.com/ICTU/quality-time/issues/985).

### Fixed

- Sorting of metrics by measurement value, target value, and status did not work. Fixes [#981](https://github.com/ICTU/quality-time/issues/981).
- Exporting tag reports to PDF did not work. Fixes [#990](https://github.com/ICTU/quality-time/issues/990).
- When using Jira as source for the issues metric, the URL to Jira in the metrics table would not work properly. Fixes [#991](https://github.com/ICTU/quality-time/issues/991).

## v1.4.0 - 2020-01-31

### Added

- Source parameter (URL's, user names, passwords, etc.) changes can be applied to different scopes: to just the source being edited or to multiple sources that have the same type and value as the one being edited. When applying the change to multiple sources, the user can change all sources (that have the same type and value) of a single metric, of a single subject, of a single report, or of all reports. Closes [#927](https://github.com/ICTU/quality-time/issues/927).
- Change logs show the users' avatars. Note that email addresses were not recorded in the change log until now, so avatars can only be shown for new changes. Closes [#948](https://github.com/ICTU/quality-time/issues/948).
- The delay for generating PDFs can be changed in the report title and can be passed to the API as parameter. Closes [#958](https://github.com/ICTU/quality-time/issues/958).

### Fixed

- The front end was still using one version 1 API. Fixes [#947](https://github.com/ICTU/quality-time/issues/947).
- Retrieving the change log would fail if not all recent changes had a change log entry. Fixes [#949](https://github.com/ICTU/quality-time/issues/949).
- After changing a value in the UI, *Quality-time* would briefly show the old value while it was updating the database. Fixes [#954](https://github.com/ICTU/quality-time/issues/954).
- Documentation API was not reachable. Fixes [#966](https://github.com/ICTU/quality-time/issues/966).

## v1.3.4 - 2020-01-15

### Fixed

- Metrics with status unknown in the details view of the 'Metrics' metric did not show a question mark. Fixes [#935](https://github.com/ICTU/quality-time/issues/935).
- Check connection for all URL and credential parameters. Fixes [#944](https://github.com/ICTU/quality-time/issues/944).

## v1.3.3 - 2020-01-15

### Fixed

- Subject cards in the report dashboard would not have a default subject title when the subject had no title. Fixes [#942](https://github.com/ICTU/quality-time/issues/942).

## v1.3.2 - 2020-01-15

### Fixed

- Metrics with status unknown in the details view of the 'Metrics' metric did not show a question mark. Fixes [#935](https://github.com/ICTU/quality-time/issues/935).

## v1.3.1 - 2020-01-15

### Fixed

- Adding sources did not work. Fixes [#939](https://github.com/ICTU/quality-time/issues/939).

## v1.3.0 - 2020-01-15

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

## v1.2.0 - 2019-12-10

### Added

- If users have a [Gravatar](https://en.gravatar.com/), it will be shown next to their username after they log in.
- REST API added for importing a complete report. Closes [#818](https://github.com/ICTU/quality-time/issues/818).
- Allow GitLab as source for the unused CI-jobs metric. Closes [#851](https://github.com/ICTU/quality-time/issues/851).

### Changed

- Open help urls in a new window or tab. Closes [#842](https://github.com/ICTU/quality-time/issues/842).

## v1.1.0 - 2019-12-03

### Fixed

- Ignore Jira fields that have no number value when summing Jira issues for the ready user story points and manual test duration metrics. Fixes [#834](https://github.com/ICTU/quality-time/issues/834).

### Added

- Added a button (expand a report title to access it) to download a PDF version of a report. The PDF report can also be downloaded via the API: `http://www.quality-time.example.org/api/v1/report/<report_uuid>/pdf`.
Closes [#828](https://github.com/ICTU/quality-time/issues/828).
- Metric summary cards now have tooltips showing the number of metrics per status (target met, target not met, etc.). Closes [#838](https://github.com/ICTU/quality-time/issues/838).

### Changed

- Show the five most recent changes in the change log table initially so that the buttons below the change log table don't disappear off screen. Each click on the "load more changes" button still loads ten more changes. Closes [#836](https://github.com/ICTU/quality-time/issues/836).

## v1.0.0 - 2019-11-28

### Fixed

- Users would not be notified of an expired session when trying to delete something while their session was expired. Fixes [#813](https://github.com/ICTU/quality-time/issues/813).
- Prevent double slashes in URLs to Jira issues. Fixes [#817](https://github.com/ICTU/quality-time/issues/817).
- Hiding metrics that do not require action did not work. Fixes [#824](https://github.com/ICTU/quality-time/issues/824).

### Added

- Store dashboard layouts on the server instead of in the local storage of the user's browser. Closes [#379](https://github.com/ICTU/quality-time/issues/379).

### Removed

- Removed deprecated metrics from metric types options. Closes [#826](https://github.com/ICTU/quality-time/issues/826).

## v0.20.0 - 2019-11-23

### Fixed

- The *Quality-time* source still used port 5001 to access the *Quality-time* API. Fixes [#806](https://github.com/ICTU/quality-time/issues/806).

### Added

- Allow for filtering metrics by metric type and source type in the *Quality-time* source. Closes [#805](https://github.com/ICTU/quality-time/issues/805).

## v0.19.1 - 2019-11-19

### Fixed

- Determining the encoding of large OWASP Dependency Check XML reports was very slow. Fixes [#803](https://github.com/ICTU/quality-time/issues/803).

## v0.19.0 - 2019-11-17

### Fixed

- Use correct API URL when accessing *Quality-time* as source. Fixes [#791](https://github.com/ICTU/quality-time/issues/791).

### Added

- Metric for manual test execution added. Closes [#556](https://github.com/ICTU/quality-time/issues/556).
- Azure DevOps can now be a source for the failing jobs metric and the unused jobs metric. Closes [#638](https://github.com/ICTU/quality-time/issues/638).

## v0.18.0 - 2019-11-12

### Fixed

- Add keep-alive messages to the server-sent events stream so it does not time out when there are no new measurements for a while. Fixes [#787](https://github.com/ICTU/quality-time/issues/787).

### Added

- In addition to a changelog per report, also keep a changelog for the reports overview. Closes [#746](https://github.com/ICTU/quality-time/issues/746).

## v0.17.0 - 2019-11-10

### Fixed

- Make string input fields with suggestions clearable. Fixes [#772](https://github.com/ICTU/quality-time/issues/772).
- Open Axe CSV files in universal newline mode. Fixes [#777](https://github.com/ICTU/quality-time/issues/777).
- Prevent browser console traceback when switching to the sources tab of a metric. Fixes [#779](https://github.com/ICTU/quality-time/issues/779).

### Added

- More flexibility in configuring LDAP by introducing a `LDAP_SEARCH_FILTER` environment variable and replacing the `LDAP_LOOKUP_USER` variable by `LDAP_LOOKUP_USER_DN`. See the [deployment instructions](deployment.md#configuring-ldap). Closes [#774](https://github.com/ICTU/quality-time/issues/774).
- Logo for Axe. Closes [#778](https://github.com/ICTU/quality-time/issues/778).

## v0.16.1 - 2019-11-07

### Fixed

- Ignoring Jenkins child jobs (jobs within pipelines) did not work. Fixes [#763](https://github.com/ICTU/quality-time/issues/763).
- Notifications from the server to the frontend about new measurements were broken after the introduction of the reverse proxy. Fixes [#765](https://github.com/ICTU/quality-time/issues/765).

## v0.16.0 - 2019-11-02

### Added

- Allow for ignoring Jenkins jobs by name or regular expression. Closes [#747](https://github.com/ICTU/quality-time/issues/747).
- For sources that are comprised of static reports, it is now possible to specify a zip file with reports as URL. *Quality-time* will unzip the file before processing its contents as normal. So far, this has been implemented for Axe CSV reports, Bandit JSON reports, JaCoCo XML reports, JUnit XML reports, NCover HTML reports, OJAudit XML reports, OpenVAS XML reports, OWASP Dependency Check XML reports, OWASP ZAP XML reports, Performancetest-runner HTML reports, Pyup.io Safety JSON reports, and Robot Framework XML reports. Closes [#748](https://github.com/ICTU/quality-time/issues/748).

## v0.15.0 - 2019-10-30

### Fixed

- The collector component would crash if an Azure DevOps source was unreachable. Fixes [#738](https://github.com/ICTU/quality-time/issues/738).
- Add a changelog entry when a user creates a report. Fixes [#742](https://github.com/ICTU/quality-time/issues/742).

### Changed

- Introduce a reverse proxy (Caddy) so that web frontend and API can both be accessed through the same port. Which is now port 80 by default. Fixes [#727](https://github.com/ICTU/quality-time/issues/727).

## v0.14.1 - 2019-10-24

### Fixed

- Login problem solved for LDAP servers where a user bind must be done. Fixes [#734](https://github.com/ICTU/quality-time/issues/734).

## v0.14.0 - 2019-10-23

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

## v0.13.0 - 2019-10-20

### Added

- *Quality-time* now counts the unmerged branches against the default branch in GitLab or Azure DevOps instead of assuming that the master branch is the default branch. Closes [#699](https://github.com/ICTU/quality-time/issues/699).

### Changed

- The "Size (LOC)" metric can now either count all lines of code or all non-commented lines of code. That means the "Size (Non-commented LOC)" metric is now deprecated. Closes [#644](https://github.com/ICTU/quality-time/issues/644).

### Fixed

- Allow for specifying an Azure DevOps repository by name. Fixes [#683](https://github.com/ICTU/quality-time/issues/683).

## v0.12.2 - 2019-10-16

### Fixed

- Remove white space at the top of the page in printouts. Fixes [#685](https://github.com/ICTU/quality-time/issues/685).
- Don't crash when the user refreshes a report in the browser. Fixes [#692](https://github.com/ICTU/quality-time/issues/692).

### Changed

- *Quality-time* now uses Python 3.8 for the collector and server components. Closes [#684](https://github.com/ICTU/quality-time/issues/684).

## v0.12.1 - 2019-10-14

### Fixed

- Allow for specifying the repository when using Azure DevOps as source for the "Source up-to-dateness" metric instead of assuming that the repository has the same name as the project. Fixes [#663](https://github.com/ICTU/quality-time/issues/663).
- Do not repeat the top menu bar in printouts, it overlaps with content. Fixes [#680](https://github.com/ICTU/quality-time/issues/680).

## v0.12.0 - 2019-10-11

### Fixed

- Because Checkmarx does not immediately return detail information, Checkmarx measurements would alternate between measurements with and without detail information, resulting in a lot of measurements in the database. Fixed by not collecting detail information from Checkmarx anymore. Fixes [#670](https://github.com/ICTU/quality-time/issues/670).
- Sources that don't need to access the network ("Calendar", "Manual number", "Random number") would throw an exception. Fixes [#672](https://github.com/ICTU/quality-time/issues/672).
- NCover reports weren't parsed correctly. Fixes [#675](https://github.com/ICTU/quality-time/issues/675).

### Removed

- *Quality-time* no longer collects detail information about security warnings from Checkmarx; the Checkmarx API is too complex, resulting in fragile interaction between *Quality-time* and Checkmarx. See [#670](https://github.com/ICTU/quality-time/issues/672).

## v0.11.0 - 2019-10-07

### Fixed

- Allow for specifying which test results (skipped, failed, errored, and/or passed) to count when using SonarQube as source for the "Tests" metric. Fixes [#634](https://github.com/ICTU/quality-time/issues/634).
- Store measurement values for each scale that a metric supports so that the graphs show correct information when the user changes the metric scale. Fixes [#637](https://github.com/ICTU/quality-time/issues/637).
- Do not stop contacting sources after receiving a 401 (Unauthorized) or 403 (Forbidden). Fixes [#652](https://github.com/ICTU/quality-time/issues/652).

### Added

- Add NCover coverage reports as source for the test coverage metrics. Closes [#636](https://github.com/ICTU/quality-time/issues/636).
- Add Azure DevOps as source for the "Tests" metric. Requires Azure Devops Server or Service 2019. Closes [#639](https://github.com/ICTU/quality-time/issues/639).
- Add Azure DevOps as source for the "Source up-to-dateness" metric. Closes [#640](https://github.com/ICTU/quality-time/issues/640).
- Add Azure DevOps as source for the "Unmerged branches" metric. Closes [#641](https://github.com/ICTU/quality-time/issues/641).
- Add percentage scale to the "Complex units", "Many parameters", "Long units", and "Suppressed violations" metrics. Closes [#645](https://github.com/ICTU/quality-time/issues/645).

## v0.10.2 - 2019-09-26

### Fixed

- Measuring the source up-to-dateness of folders in GitLab did not work. Fixes [#626](https://github.com/ICTU/quality-time/issues/626).

## v0.10.1 - 2019-09-25

### Fixed

- Measuring size (LOC), size (non-commented LOC), tests, and failed tests using SonarQube as source would fail with a parse error. Fixes [#623](https://github.com/ICTU/quality-time/issues/623).

## v0.10.0 - 2019-09-22

### Added

- All metrics now have an explicit scale that's either fixed to "Count" or "Percentage", or that can be changed from "Count to "Percentage" and vice versa. Metrics whose scale can be changed: "Duplicated lines", "Metrics", "Test branch coverage", and "Test line coverage". Closes [#504](https://github.com/ICTU/quality-time/issues/504).
- Added a 'landing URL' parameter to some sources so *Quality-time* can refer users to a human readable version of a machine readable report. For example, you can add an HTML version of a JaCoCo report to a JaCoCo XML report source. Closes [#554](https://github.com/ICTU/quality-time/issues/554).

## v0.9.1 - 2019-09-10

### Fixed

- To prevent reporting Checkmarx internal server errors to users when reports are unexpectedly unavailable, don't immediately remove a Checkmarx report after reading it, but silently ignore a removed report and create a new one. Fixes [#468](https://github.com/ICTU/quality-time/issues/468).
- Prevent locked accounts by not contacting a source again after receiving a 401 (unauthorized) or 403 (forbidden) HTTP status, until the metric's configuration changes. Fixes [#604](https://github.com/ICTU/quality-time/issues/604).

## v0.9.0 - 2019-09-06

### Added

- The direction of metrics is now configurable. The direction of a metric determines whether smaller measurements are better, or bigger measurements are better. This means that the "number of tests" metric, with its direction reversed, can now also be used to measure the number of failing tests. The "failing tests" metric is deprecated. Closes [#552](https://github.com/ICTU/quality-time/issues/552).
- Metrics can be reordered. Expand a metric to show the reordering buttons on the lower left-hand side of the metric details. The buttons allow one to move a metric to the top of the table, to the previous row, to the next row, and to the bottom of the table. Closes [#585](https://github.com/ICTU/quality-time/issues/585).

### Fixed

- Checkmarx internal server error solved. Fixes [#468](https://github.com/ICTU/quality-time/issues/468).
- Use a consistent style for labels of input fields. Fixes [#579](https://github.com/ICTU/quality-time/issues/579).
- Added *Quality-time* logo to the *Quality-time* source. Fixes [#580](https://github.com/ICTU/quality-time/issues/580).
- When adding HQ as source for the accessibility metric, show the URL and metric id parameters. Fixes [#587](https://github.com/ICTU/quality-time/issues/587).
- The layout of the reports overview dashboard would be reset after visiting a tag report. Fixes [#588](https://github.com/ICTU/quality-time/issues/588).
- Tag report donut charts were always white. Fixes [#589](https://github.com/ICTU/quality-time/issues/589).

## v0.8.2 - 2019-08-28

### Fixed

- Prevent web browsers from automatically filling in username and password in the source configuration tab. Fixes [#574](https://github.com/ICTU/quality-time/issues/574).

## v0.8.1 - 2019-08-28

### Fixed

- Changing the subject type now changes the subject name if the default subject name has not been overridden. Fixes [#553](https://github.com/ICTU/quality-time/issues/553).
- When a user changes a password field, don't show the old password in the change log unmasked. Fixes [#565](https://github.com/ICTU/quality-time/issues/565).
- Use <= and >= for the metric direction in the metric tables instead of < and >. Fixes [#567](https://github.com/ICTU/quality-time/issues/567).

## v0.8.0 - 2019-08-23

### Added

- Add meta metrics and the ability to add *Quality-time* itself as source for the meta metrics. Closes [#337](https://github.com/ICTU/quality-time/issues/337).
- Accessibility metric for Axe report source added. Closes [#338](https://github.com/ICTU/quality-time/issues/338).

### Fixed

- Don't use the unicode characters for <= and >= in the source code; it caused problems on Windows. Fixes [#558](https://github.com/ICTU/quality-time/issues/558).

## v0.7.1 - 2019-08-18

### Fixed

- When generating keys for OWASP ZAP security warnings, strip any hashes from the application urls to ensure the keys are stable. Fixes [#541](https://github.com/ICTU/quality-time/issues/541).
- In addition to version 2.0 also support version 2.1 and 2.2 of the OWASP Dependency Check XML format. Fixes [#543](https://github.com/ICTU/quality-time/issues/543).

## v0.7.0 - 2019-08-14

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

## v0.6.0 - 2019-08-11

### Added

- Keep track of changes made by users in a change log. The change log for a report can be viewed by expanding the report title. The change log for a subject can be viewed by expanding the subject title. The change logs for metric and their sources be viewed by expanding the metric. Closes [#285](https://github.com/ICTU/quality-time/issues/285).
- When the user session is expired (after 24 hours) log out the user and notify them of the expired session. Closes [#373](https://github.com/ICTU/quality-time/issues/373).
- Added a metric for measuring the duration of manual tests. Added Jira as default source for the metric. Closes [#481](https://github.com/ICTU/quality-time/issues/481).

### Fixed

- When using OWASP ZAP reports as source for the security warnings metric, report on the number of "instances" instead of "alert items". Fixes [#467](https://github.com/ICTU/quality-time/issues/467).
- Don't wait 15 minutes before trying to access a requested Checkmarx SAST XML report, but try again after one minute. Partial fix for [#468](https://github.com/ICTU/quality-time/issues/468).
- The Performancetest-runner now uses "scalability" instead of "ramp-up" as name for the scalability measurement. Closes [#480](https://github.com/ICTU/quality-time/issues/480).
- OJAudit XML files may contain duplicate violations (i.e. same message, same severity, same model, same location, same everything) which led to problems in the user interface. Fixed by merging multiple duplication violations and adding a count field to the violations. Fixes [#515](https://github.com/ICTU/quality-time/issues/515).
- Use Jenkins job timestamp for the source up-to-dateness metric if the Jenkins test report doesn't contain timestamps in the test report itself. Fixes [#517](https://github.com/ICTU/quality-time/issues/517).
- Stop sorting metrics when the user adds a new metric to prevent it from jumping around due to the sorting. Fixes [#518](https://github.com/ICTU/quality-time/issues/518).

## v0.5.1 - 2019-07-18

### Fixed

- The Trello parameter "lists to ignore" was not displayed properly. Fixes [#471](https://github.com/ICTU/quality-time/issues/471).
- The number of issues would not be measured if the source was Jira. Fixes [#475](https://github.com/ICTU/quality-time/issues/475).

## v0.5.0 - 2019-07-16

### Added

- Added Pyup.io Safety JSON reports as possible source for the security warnings metric. Closes [#450](https://github.com/ICTU/quality-time/issues/450).
- Added Bandit JSON reports as possible source for the security warnings metric and the source up-to-dateness metric. Closes [#454](https://github.com/ICTU/quality-time/issues/454).
- Only measure metrics that have all mandatory parameters supplied. Closes [#462](https://github.com/ICTU/quality-time/issues/462).

### Fixed

- Add performance test stability and scalability metrics to the example report. Fixes [#447](https://github.com/ICTU/quality-time/issues/447).
- Set up a new LDAP connection for each authentication in an attempt to prevent a "Broken pipe" between *Quality-time* and the LDAP server. Fixes [#469](https://github.com/ICTU/quality-time/issues/469).

## v0.4.1 - 2019-07-08

### Fixed

- Frontend can't reach server.

## v0.4.0 - 2019-07-07

### Changed

- Run server on port 5001 instead of 8080 to reduce chances of interfering with other applications.
- Allow for deployments where the different components all have the same hostname, e.g. quality-time.example.org, and only the ports differ.

## v0.3.0 - 2019-07-05

### Added

- Metric for performance test duration added. Closes [#401](https://github.com/ICTU/quality-time/issues/401).
- Metric for performance test stability added. Closes [#433](https://github.com/ICTU/quality-time/issues/433).
- Metric for performance scalability added. Closes [#434](https://github.com/ICTU/quality-time/issues/434).
- [Performancetest-runner](https://github.com/ICTU/performancetest-runner) reports can now be used as metric source for the tests and failed tests metrics. Closes [#402](https://github.com/ICTU/quality-time/issues/402).

## v0.2.3 - 2019-07-01

### Fixed

- Time travelling to a date before any report existed would throw an exception on the server. Fixes [#416](https://github.com/ICTU/quality-time/issues/416).
- Trend graphs would be too tall and overlap with the next metric. Fixes [#420](https://github.com/ICTU/quality-time/issues/420).
- When clicking the report date field in the menu bar, the calendar popup would be displayed at the wrong location before popping up at the right location. Fixes [#424](https://github.com/ICTU/quality-time/issues/424).

## v0.2.2 - 2019-06-28

### Fixed

- Version number was missing in the footer of the frontend. Fixes [#410](https://github.com/ICTU/quality-time/issues/420).

## v0.2.1 - 2019-06-26

### Fixed

- Work around a limitation of the Travis configuration file. The deploy script does not allow sequences, which is surprising since scripts in other parts of the Travis configuration file do allow sequences. See [https://github.com/travis-ci/dpl/issues/673](https://github.com/travis-ci/dpl/issues/673).

## v0.2.0 - 2019-06-26

### Added

- Release Docker containers from [Travis CI](https://travis-ci.org/ICTU/quality-time) to [Docker Hub](https://hub.docker.com/search?q=quality-time_&type=image).

## v0.1.0 - 2019-06-24

### Added

- Initial release consisting of a metric collector, a web server, a frontend, and a database component.
