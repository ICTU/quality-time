# User manual

```{note}
This user manual assumes *Quality-time* has been installed, is up and running, and that you have opened *Quality-time* in your browser.
```

## {index}`Logging in` and {index}`out <Logging out>`

Quality reports can be viewed without logging in, but to edit reports and metrics you need to be logged in. Click the "Login" button in the menu bar:

![Logged out screenshot](screenshots/menubar_logged_out.png)

Enter your {index}`LDAP`-credentials in the dialog:

```{image} screenshots/login_dialog.png
:alt: Loging dialog with username and password fields
:width: 400px
:align: center
```

```{note}
You can either use your canonical LDAP name as username or your LDAP user id. Please contact your system administrator if you don't know your LDAP credentials.
```

```{index} Gravatar
```

After hitting "Submit" you should be logged in. The menu bar shows your username. If you have a [Gravatar](https://en.gravatar.com/), it will be shown next to your username.

![Logged in screenshot](screenshots/menubar_logged_in.png)

Clicking "Logout" logs you out from *Quality-time*. Your user session expires after 24 hours and you need to log in again to be able to edit reports.

```{index} Permissions
```

## Configuring permissions

*Quality-time* implements a simple permissions system. Anybody (authenticated and not authenticated) can always view all the information in *Quality-time*. By default, anybody who is logged in can edit reports, subjects, metrics, sources and measured entities. However, this access can be restricted to certain users. On the homepage, expand the reports overview title to see two input fields to grant users report editing rights or entity editing rights.

### Report edit permission

Report edit permission allows a user to edit the reports in this *Quality-time* instance. That means to edit the add, edit, and delete reports, subjects, metrics, and sources.

If you forget to add yourself, your username will be added automatically. This means that you can't retract your own report editing rights: add another user and ask them to remove your username or email address.

To restore the default situation where every logged-in user can edit reports, subjects, metrics, and sources, simply remove all usernames and email addresses.

### Entity edit permission

Entity edit permission will allow a user to update the status of measured entities. A user with this permission can for example mark violations as false positives.

Unlike for the report edit permission, it is possible to retract yourself from the list of entity editors.

To restore the default situation where every logged-in user can edit entities, simply remove all usernames and email addresses.

## Configuring quality reports

Each *Quality-time* instance can serve multiple quality reports. A quality report consists of one or more subjects - things such as software products, projects, and processes - that you want to measure the quality of. Each subject has one or more metrics that tell you something about the quality of the subject. For example, the number of failing test cases of an application, or the number of ready user story points for a Scrum team. To collect the measurement data, each metric has one or more sources that *Quality-time* will use to measure the metric.

```{attention}
You need to be logged in to be able to edit quality reports.
```

```{index} Report
```

### Configuring reports

#### Adding reports

To add a new report, be sure to be logged in and click the "Add report" button on the home page. This will create a new empty report. Click the report card in the dashboard to navigate to it.

#### Editing reports

To change the title or subtitle of a report, expand the report header and simply enter a new title and/or subtitle in their respective fields. For notifications, see the [Notifications](#notifications) section below.

![Editing report screenshot](screenshots/editing_report.png)

#### Deleting reports

To delete a report expand the report header and click the "Delete report" button. The report and all its subjects is deleted.

```{danger}
Be careful, there's no way to undo your action via the user interface.
```

```{index} Subject
```

### Configuring subjects

#### Adding subjects

![Adding subject screenshot](screenshots/adding_subject.png)

Each quality report consists of "subjects". Subjects are the things being measured by *Quality-time*. A subject can be a software product or component, a software process, or whatever you like. To add a new subject, be sure you are logged in and are on a report page. Click the "Add subject" button to add a new subject. The subject is added to the report dashboard.

Alternatively, you can also copy an existing subject or move an existing subject to the report. Clicking the "Copy subject" or "Move subject" button shows a drop down menu with all of the subjects to choose from. Copying or moving a subject also copies or moves the metrics and sources of the subject.

#### Editing subjects

To change the subject type and name expand the subject header if it's not already expanded. The subject type can be changed by means of the "Subject type" dropdown.

![Editing subject screenshot](screenshots/editing_subject.png)

```{note}
Currently, changing the type of the subject does not affect what you can do with the subject.
```

To change the name of the subject, simply type the new name in the "Subject name" field and hit enter.

#### Deleting subjects

To delete a subject expand the subject header and click the "Delete subject" button. The subject and all its metrics is deleted.

```{danger}
Be careful, there's no way to undo your action via the user interface.
```

```{index} Metric
```

### Configuring metrics

#### Adding metrics

To add a metric to a subject, hit the "Add metric" button to create a new metric.

![Adding metric screenshot](screenshots/adding_metric.png)

*Quality-time* adds a metric to the report that you can next configure. It's immediately displayed in the metric table (and in the report dashboard) as white and with a question mark because *Quality-time* has no data on this metric yet.

Alternatively, you can also copy an existing metric or move an existing metric to the subject. Clicking the "Copy metric" or "Move metric" button shows a drop down menu with all of the metrics to choose from. Copying or moving a metric also copies or moves the sources of the metric.

#### Editing metrics

After you've added a metric, the metric is visible in the subject's metric table. You can change the metric configuration in the metric tab.

![Editing metric screenshot](screenshots/editing_metric.png)

The first parameter is the "Metric type". The metric type determines what gets measured. When you change the metric type, the sources you can select in the "Sources" tab change accordingly. See the overview of [supported metrics and sources](metrics_and_sources.md) for the list of supported metric types. By default, the name of the metric is equal to its type, "Accessibility violations" in the example above, but you can change the metric name using the "Metric name" field.

Metrics can have zero or more arbitrary "{index}`Tags <Tag>`". Most metric have a default tag, but you can remove it and/or add more if you like. For each tag, the report dashboard at the top of the page shows a summary of the metrics with that tag:

![Dashboard tags](screenshots/dashboard_tags.png)

The "Metric {index}`scale <Scale>`" field determines what scale to use to measure the metric. All metrics currently support either the "Count" scale, or the "Percentage" scale, or both. In the example of the duplicated lines metric above, setting the metric scale to "Percentage" means that the percentage of lines that are duplicated is shown instead of the count of duplicated lines.

The "Metric {index}`direction <Direction>`" determines whether lower measurement values are considered to be better or worse. Usually, the default direction is correct. An example of a metric where you might want to change the direction is the "tests" metric. When used to measure the number of tests, more tests is better. But, when used to measure the number of failing tests, fewer is better.

The "Metric {index}`unit <Unit>`" derives its default value from the metric type. Override as needed.

The "Metric {index}`target <Target>`" determines at what value a measurement is below or above target. In the example below only measurement values of 0 are on target. The "Metric near target" determines when the measurement value is sufficiently close to the target to no longer require immediate action. Metrics near their target are yellow.

If a metric doesn't meet the target value, but your team isn't able to fix the situation in the short run, you can accept the deviation as *{index}`technical debt <Technical debt>`*. Set the "Accept technical debt?" field to "Yes" and enter the value you're accepting for the time being in the "Metric debt target" field. If you want to pay off the debt before a certain date, this can be registered in the "Metric debt end date" field.

The "{index}`Comment`" field can be used to capture the rationale for accepting technical debt, or any other information. HTML and URLs are supoorted.

#### Reordering metrics

To reorder metrics, expand the metric in the metric table and use the buttons on the lower left-hand side to move the metric one row higher or lower, or to the top or bottom of the table. The order is saved on the server. Users can temporarily override the default ordering of the metrics by clicking the column headers thus sorting by e.g. name or status.

#### Deleting metrics

To delete a metric, expand the metric in the metric table and click the "Delete metric" button. The metric and its sources are deleted.

```{danger}
Be careful, there's no way to undo your action via the user interface.
```

```{index} Source
```

### Configuring sources

#### Adding sources

To add a source to a metric, expand the metric in the metric table and then click the "Sources" tab. In the "Sources" tab, click the "Add source" button. This adds one of the sources that can support the metric type. See the overview of [supported metrics and sources](metrics_and_sources.md) for the list of supported source types.

![Adding source screenshot](screenshots/adding_source.png)

Alternatively, you can also copy an existing source or move an existing source to the metric. Clicking the "Copy source" or "Move source" button shows a drop down menu with all of the sources to choose from.

If you add multiple sources for one metric the measurement values of each source are combined to get one measurement value for the metric. Usually this means adding up the values, but for some metrics this doesn't make sense and the minimum or maximum value of the sources is used as the metric value.

#### Editing sources

After you've added a source, you can change the source type using the "Source type" drop-down menu. The available source types depend on the metric type. E.g. OWASP Dependency Check supports the security warnings metric type, but GitLab does not so GitLab is not shown.

By default, the name of the source equals the source type but this can be overridden using the "Source name" field.

The parameters that sources need differ per source type. Most sources need a URL, and optionally take either a username and password or a token so that *Quality-time* can access the source. If a parameter is required, this is indicated with a red outline as shown below.

![Editing source screenshot](screenshots/editing_source.png)

Source parameter (URL's, usernames, passwords, etc.) changes can be applied to different scopes: to just the source being edited or to multiple sources that have the same type and value as the one being edited. When applying the change to multiple sources, the user can change all sources that have the same type and value of a metric, of a subject, of a report, or of all reports.

#### Deleting sources

To delete a metric's source, expand the metric in the metric table, select the "Sources" tab and click the "Delete source" button. The source is deleted and no longer used to measure the metric.

```{danger}
Be careful, there's no way to undo your action via the user interface.
```

```{index} Entity
```

### Configuring entities

An entity is a measured entity like for example one single failed job in GitLab for a metric that measures failed GitLab jobs or a single violation in SonarQube for a metric that measures violations. What exactly an entity is, and what properties it has depends on what the metric in question is measuring. Not every metric will have entities.

To add a source to a metric, expand the metric in the metric table and then click the tab with the source name. It will show a list of entities with all its details.

When clicking on one of the entities, it can be expanded and edited. Options are for example mark an entity as false positive or as fixed. Every action can be enriched with a comment for explanation.

## Notes on specific metrics

```{index} Metrics
```

### Merge requests

The merge requests metric reports the number of merge requests. Currently, GitLab and Azure DevOps can be configured as source for this metric.

In itself, the number of merge requests is not indicative of software quality. However, by setting the parameter "Minimum number of upvotes", the metric can report on merge requests that have fewer than the minimum number of upvotes. The parameter "Merge request state" can be used to exclude e.g. closed merge requests. The parameter "Target branches to include" can be used to further limit the merge requests to only count merge requests that target specific branches, e.g. the "develop" branch.

### Metrics

One special metric type is "Metrics". It counts the number of metrics in a quality report. This makes it possible to create 'meta'-reports that for example measure the number of security metrics that don't meet their target.

After adding *Quality-time* as a source to a "Metrics"-metric, one can configure which statuses to count and which metrics to consider by filtering on report names or identifiers, on metric types, on source types, and on tags.

![Editing *Quality-time* source screenshot](screenshots/editing_quality_time_source.png)

Note that when the "Metrics" metric is itself part of the set of metrics it counts, a peculiar situation may occur: when you've configured the "Metrics" to count red metrics and its target is not met, the metric itself will become red and thus be counted as well. For example, if the target is at most five red metrics, and the number of red metrics increases from five to six, the "Metrics" value will go from five to seven. You can prevent this by making sure the "Metrics" metric is not in the set of counted metrics, e.g. by putting it in a different report and only count metrics in the other report(s).

```{index} Unmerged branches
```

### Test cases

The test cases metric reports on the number of test cases, and their test results. The test case metric is different than other metrics because it combines data from two types of sources: it needs one or more sources for the test cases, and one or more sources for the test results. The test case metric then matches the test results with the test cases.

Currently, only Jira is supported as source for the test cases. JUnit and TestNG are supported as source for the test results. So, to configure the test cases metric, you need to add at least one Jira source and one JUnit or one TestNG source. In addition, to allow the test case metric to match test cases from Jira with test results from the JUnit and/or TestNG XML files, the test results should mention Jira issue keys in their title or description. 

For example, suppose you have configured Jira with the JQL: `project = "My Project" and type = "Logical Test Case"` and this results in these test cases:

| Key  | Summary     |
|------|-------------|
| MP-1 | Test case 1 |
| MP-2 | Test case 2 |
| MP-3 | Test case 3 |

Also suppose your JUnit XML has the following test results:

```xml
<testsuite tests="5" errors="0" failures="1" skipped="1">
    <testcase name="MP-1; step 1">
        <failure />
    </testcase>
    <testcase name="MP-1; step 2">
        <skipped />
    </testcase>
    <testcase name="MP-2">
        <skipped />
    </testcase>
    <testcase name="MP-3; step 1"/>
    <testcase name="MP-3; step 2"/>
</testsuite>
```

The test case metric will combine the JUnit XML file with the test cases from Jira and report one failed, one skipped, and one passed test case:

| Key  | Summary     | Test result |
|------|-------------|-------------|
| MP-1 | Test case 1 | failed      |
| MP-2 | Test case 2 | skipped     |
| MP-3 | Test case 3 | passed      |

If multiple test results in the JUnit or TestNG XML file map to one Jira test case (as with MP-1 and MP-3 above), the "worst" test result is reported. Possible test results from worst to best are: errored, failed, skipped, and passed. 

### Unmerged branches

The unmerged branches metric reports on the number of branches that have not been merged back to the default branch in the version control system. Currently, GitLab and Azure DevOps can be configured as source for this metric.

The "master"-branch is the default branch in both GitLab and Azure DevOps. This means that a branch is considered unmerged if it has not been merged with master. If you want to use a different branch as default branch, you need to configure this in the source, see the documentation for [GitLab](https://docs.gitlab.com/ee/user/project/repository/branches/default.html) or [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops#change-your-default-branch).

To ignore branches that people are actively working on, use the "Number of days since last commit after which to consider branches inactive"-parameter.

```{index} Merge requests
```

## Notes on specific sources

```{index} GitLab
```

### GitLab

Some metric sources are documents in JSON, XML, CSV or HTML format. Examples include JUnit XML reports, Jacoco XML reports and Axe CSV reports. If such a document is stored in GitLab, *Quality-time* needs to use the GitLab API to retrieve the report. This means you need to provide the correct GitLab API URL to *Quality-time*.

There are two scenarios: the source is a build artifact of a GitLab CI pipeline, or the source is stored in a GitLab repository.

#### GitLab CI pipeline build artifact

When the metric source is a build artifact of a GitLab CI pipeline, use [URLs of the following format](https://docs.gitlab.com/ee/api/job_artifacts.html#download-a-single-artifact-file-from-specific-tag-or-branch):

`https://<gitlab-server>/api/v4/projects/<project-id>/jobs/artifacts/<branch>/raw/<path>/<to>/<file-name>?job=<job-name>`

The project id can be found under the [project's general settings](https://docs.gitlab.com/ee/user/project/settings/).

If the repository is private, you also need to enter an [personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) with the scope "read_api" in the private token field.

#### GitLab repository file

When the metric source is a file stored in a GitLab repository, use [URLs of the following format](https://docs.gitlab.com/ee/api/repository_files.html#get-raw-file-from-repository):

`https://<gitlab-server>/api/v4/projects/<project-id>/repository/files/<file-path-with-slashes-%2F-encoded>/raw?ref=<branch>`

The project id can be found under the [project's general settings](https://docs.gitlab.com/ee/user/project/settings/).

If the repository is private, you also need to enter an [personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) with the scope "read_repository" in the private token field.

```{index} Jenkins
```

```{index} Jenkins test report
```

```{index} JaCoCo Jenkins plugin
```

```{index} OWASP Dependency Check Jenkins plugin
```

### Jenkins, Jenkins test report, JaCoCo Jenkins plugin, and OWASP Dependency Check Jenkins plugin

To authorize *Quality-time* for (non-public resources in) Jenkins, you can either use a username and password or a username and [API token](https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/). Note that, unlike other sources, when using the API token Jenkins also requires the username to which the token belongs.

```{index} Security warnings metric
```

```{index} Generic JSON format for security warnings
```

### Generic JSON format for security warnings

In some cases, there are security vulnerabilities not found by automated tools. Quality-time has the ability to parse security warnings from JSON files with a simple generic format.

The JSON format consists of an object with one key `vulnerabilities`. The value should be a list of, you guess it, vulnerabilities. Each vulnerability is an object with three keys: `title`, `description`, and `severity`. The title and description values should be strings. The severity is also a string and can be either `low`, `medium`, or `high`.

Example generic JSON file:

```json
{
    "vulnerabilities": [
        {
            "title": "ISO27001:2013 A9 Insufficient Access Control",
            "description": "The Application does not enforce Two-Factor Authentication and therefore not satisfy security best practices.",
            "severity": "high"
        },
        {
            "title": "Threat Model Finding: Uploading Malicious of Malicious files",
            "description": "An attacker can upload malicious files with low privileges can perform direct API calls and perform unwanted mutations or see unauthorized information.",
            "severity": "medium"
        }
    ]
}
```

## Customizing quality reports

Users can customize quality reports on an individual basis by changing the dashboard layout, by filtering metrics, and by filtering metric entities.

```{index} Dashboard
```

### Customizing dashboards

Both the reports dashboard on the *Quality-time* landing page and the dashboard of individual projects can be customized by dragging and dropping the cards. The dashboard layout is persisted in the database and thus shared with other users.

```{index} Trend table
```

### Subject trend table

By default, subjects show the current measurement value of each metric, together with other details such as the target value, comments and tags. Subjects can also show multiple recent measurement values of each metric in the form of a trend table. Use the 'hamburger' menu on the top left-hand side of the metric table to switch between the 'details' and 'trend table' views.  The hamburger menu can also be used to show more or fewer dates and to configure the number of weeks between dates.

### Sorting metrics

Metrics can be sorted by clicking on the table column headers. The sort order cycles between the default order, sorted ascending by the column click, and sorted descending by the column clicked.

```{index} Tag
```

### Filtering metrics by tag

In a report's dashboard, click on a tag card to show only metrics that have the selected tag. The selected tag turns blue to indicate it is filtered on. Click the selected tag again to turn off the filtering. Selecting multiple tags shows metrics that have at least one of the selected tags.

### Filtering metrics by status

Each metric table has a 'hamburger' menu on the top left-hand side that can be used to hide metrics that need no action.

![Metric table columns](screenshots/metric_table_columns.png)

### Hiding columns

Each metric table has a 'hamburger' menu on the top left-hand side that can be used to hide specific columns from the metric tables.

```{index} Export report
```

```{index} PDF
```

## Export reports as PDF

*Quality-time* reports can be downloaded as PDF. To create PDFs, *Quality-time* has a rendering service included to convert the HTML report into PDF.

As *Quality-time* has to open the report in a (headless) browser and load all the metrics, creating the PDF can take some time. Especially for big reports.

### Manually

To manually download a PDF version of a report, navigate to the report and expand the report's title. Click the "Download report as PDF" button to create and download the PDF report.

The exported PDF report has the same metric table rows and columns hidden as in the user interface, and has the same metrics expanded as in the user interface. The exported PDF report also has the same date as the report visible in the user interface.

### Via the API

If the PDF report needs to be downloaded programmatically, e.g. for inclusion in a release package, use the API: `http://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf`. No authorization is needed for this API.

The `report_uuid` is the unique identifier that *Quality-time* assigns to a report. It can be found by navigating to a report in the browser and looking for the `report_uuid` in the address bar. For example, when the URL in the browser's address bar is `http://www.quality-time.example.org/f1d0e056-2440-43bd-b640-f6753ccf4496?hidden_columns=comment`, the part between the last slash and the question mark is the `report_uuid`.

To hide metrics that do not need any action, set the `hide_metrics_not_requiring_action` parameter to true, i.e. `http://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?hide_metrics_not_requiring_action=true`.

To hide columns from the report, set the `hidden_columns` parameter, for example `http://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?hidden_columns=target,comment`. Possible options are `trend`, `status`, `measurement`, `target`, `source`, `comment`, and `tags`.

To expand metrics and set the active tab of the metric detail information, use the `tabs` parameter, i.e. `http://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?tabs=<metric_uuid>:<tab_index>,<metric_uuid>:<tab_index>,...`. The metric UUID can be found by navigating to a report in the browser, expanding the metric, and looking for the `tabs` parameter in the address bar. For example, when the URL in the browser's address bar is `http://www.quality-time.example.org/1d0e056-2440-43bd-b640-f6753ccf4496?tabs=d4c0dea1-b072-417f-804e-6045544748db:0`, the part between the equal sign and the colon is the metric UUID of the expanded metric. The number after the colon is the number of the active tab, e.g. 0 is the metrics configuration tab, 1 is the source configuration tab, 2 is the trend graph, etc.

The use the subject trend table view instead of the default details view, use the `subject_trend_table` parameter and set it to true, for example `http://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?subject_trend_table=true`.

To change the number of dates and the time between dates shown in the trend table, use the `trend_table_nr_dates` and the `trend_table_interval` parameters. The number of dates should be an integer between 2 and 7. The interval should be an integer between 1 and 4 and is in weeks.

To export an older version of a report, add the `report_date` parameter with a date value in ISO-format (YYYY-MM-DD), for example `http://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?report_date=2020-09-01`.

```{index} Export report
```

```{index} Import report
```

## Export and import reports as JSON

*Quality-time* provides functionality for importing and exporting reports in JSON format. This functionality can be used for backing up reports or for transferring reports from one *Quality-time* instance to another one. Currently, this functionality is only available via the API, with one endpoint for importing and one for exporting the JSON reports.

A *Quality-time* report in JSON format contains the latest configuration of the report, with all its subjects, metrics and sources. It does not contain any actual measurements. The credentials of configured sources are encrypted on export to protect sensitive data.

To use the import and export endpoints you need to be authenticated. For example, using curl:

```console
curl --cookie-jar cookie.txt --request POST --header "Content-Type: application/json" --data '{"username": "jadoe", "password": "secret"}' http://quality-time.example.org/api/v3/login
```

### Export API

The exporting endpoint is available via `http://www.quality-time.example.org/api/v3/report/<report-uuid>/json?public_key=<public-key>`. The exporting endpoint returns JSON content only.

For example, using curl, and assuming you have logged in as shown above:

```console
curl --cookie cookie.txt --output export.json http://quality-time.example.org/api/v3/report/97b2f341-45ce-4f2b-9a71-3675f2f54cf7/json 
```

The `report_uuid` is the unique identifier that *Quality-time* assigns to a report. It can be found by navigating to a report in the browser and looking for the `report_uuid` in the address bar. For example, when the URL in the browser's address bar is `http://www.quality-time.example.org/f1d0e056-2440-43bd-b640-f6753ccf4496?hidden_columns=comment`, the part between the last slash and the question mark is the `report_uuid`.

The {index}`public key <Public key>` argument is optional. If no public key is provided, the public key of the exporting *Quality-time* instance is used for encrypting the source credentials. If the report needs to be imported in a different *Quality-time* instance, the public key of that instance should be provided. It can be obtained at `www.quality-time.example.org/api/v3/public_key`. The exported JSON report can only be imported into the *Quality-time* whose public key has been used for the encryption of credentials during the export.

### Import API

The importing endpoint is available via `http://www.quality-time.example.org/api/v3/report/import`. The import endpoint accepts JSON content only. See the [example reports](https://github.com/ICTU/quality-time/tree/master/components/server/src/example-reports) for the format.

For example, using curl, and assuming you have logged in as shown above:

```console
$ curl --cookie cookie.txt --request POST --header "Content-Type: application/json" --data @report-to-import.json http://quality-time.example.org/api/v3/report/import
{"ok": true, "new_report_uuid": "97a3e341-44ce-4f2b-4471-36e5f2f34cf6"}
```

On import, all UUID's contained in the report (UUID's of the report, subjects, metrics and sources) will be replaced to prevent conflicts if the report already exists.

If the report contains encrypted credentials, the importing *Quality-time* instance will decrypt the credentials using its public key. Note that if the credentials were encrypted using the public key of a different *Quality-time* instance, an error will occur, and the import will fail.

To allow for seeding a *Quality-time* instance with default reports, imported reports may contain unencrypted credentials. These unencrypted credentials will be imported unchanged.

```{index} Notification
```

## Notifications

*Quality-time* can send notifications about metrics that change status to {index}`Microsoft Teams` channels. To enable notifications for a report, expand the report header and paste a [Microsoft Teams webhook](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook).

If a {index}`webhook <Webhook>` has been configured, *Quality-time* will check for changes in the status of metrics every minute. As soon as one or more metrics in the report change status, a notification will be sent to the Microsoft Teams channel configured by the webhook.

*Quality-time* sends a notification when the status of a metric changes as well as when the status of a metric has been the same for three weeks.
