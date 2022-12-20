# User manual

```{note}
This user manual assumes *Quality-time* has been installed, is up and running, and that you have opened *Quality-time* in your browser. See the [](deployment.md) on how to deploy *Quality-time*.
```

## {index}`Logging in` and {index}`out <Logging out>`

You can view Quality reports without logging in, but to edit reports and metrics you need to log in. Click the "Login" button in the menu bar:

![Logged out screenshot](screenshots/menubar_logged_out.png)

Enter your {index}`LDAP`-credentials in the dialog:

```{image} screenshots/login_dialog.png
:alt: Login dialog with username and password fields
:class: only-light
:width: 400px
:align: center
```

```{image} screenshots/login_dialog_dark.png
:alt: Login dialog with username and password fields
:class: only-dark
:width: 400px
:align: center
```

```{note}
You can either use your canonical LDAP name as username or your LDAP user id. Please contact your system administrator if you don't know your LDAP credentials.
```

```{index} Gravatar
```

After hitting "Submit" you should be logged in. The menu bar shows your username. If you have a [Gravatar](https://en.gravatar.com/), it will be displayed next to your username.

![Logged in screenshot](screenshots/menubar_logged_in.png)

Clicking "Logout" logs you out from *Quality-time*. Your user session expires after 24 hours and you need to log in again to be able to edit reports.

```{index} Permissions
```

## Configuring permissions

*Quality-time* implements a limited permissions system. Anybody (authenticated and not authenticated) can always view all the information in *Quality-time*. By default, anybody who is logged in can edit reports, subjects, metrics, sources and measured entities. However, this access can be restricted to certain users. On the homepage, expand the reports overview title to see two input fields to grant users report editing rights or entity editing rights.

### Report edit permission

Report edit permission allows a user to edit the reports in this *Quality-time* instance. That means to edit the add, edit, and delete reports, subjects, metrics, and sources.

If you forget to add yourself, your username will be added automatically. This means that you can't retract your own report editing rights: add another user and ask them to remove your username or email address.

To restore the default situation where every logged-in user can edit reports, subjects, metrics, and sources, remove all usernames and email addresses.

### Entity edit permission

Entity edit permission will allow a user to update the status of measured entities. A user with this permission can for example mark violations as false positives.

Unlike for the report edit permission, it's possible to retract yourself from the list of entity editors.

To restore the default situation where every logged-in user can edit entities, remove all usernames and email addresses.

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

To change the title or subtitle of a report, expand the report header and enter a new title and/or subtitle in their respective fields. For the desired reaction times, see the [Customizing quality reports](#customizing-quality-reports) section below. For the issue tracker, see the [Issue tracker](#issue-tracker) section below. For notifications, see the [Notifications](#notifications) section below.

The "{index}`Comment <pair: Comment;Report>`" field can be used to describe the report, or any other information. HTML and URLs are supported. The entered comments are shown between the report title and the dashboard.

```{image} screenshots/editing_report.png
:alt: Screenshot of dialog to edit report title, subtitle, and comments
:class: only-light
```

```{image} screenshots/editing_report_dark.png
:alt: Screenshot of dialog to edit report title, subtitle, and comments
:class: only-dark
```

#### Deleting reports

To delete a report expand the report header and click the "Delete report" button. The report and all its subjects is deleted.

```{danger}
Be careful, there's no way to undo your action via the user interface.
```

```{index} Subject
```

### Configuring subjects

#### Adding subjects

```{image} screenshots/adding_subject.png
:alt: Screenshot of buttons to add subjects to a report
:class: only-light
```

```{image} screenshots/adding_subject_dark.png
:alt: Screenshot of buttons to add subjects to a report
:class: only-dark
```

Each quality report consists of "subjects". Subjects are the things being measured by *Quality-time*. A subject can for example be a software product or component, a software process, or a continuous integration pipeline.

```{seealso}
See the [reference manual](reference.md) for the list of supported subject types.
```

To add a new subject, be sure you are logged in and are on a report page. Click the "Add subject" button to select a subject type and add a new subject. The subject is added to the report dashboard.

Alternatively, you can also copy an existing subject or move an existing subject to the report. Clicking the "Copy subject" or "Move subject" button shows a drop down menu with all of the subjects to choose from. Copying or moving a subject also copies or moves the metrics and sources of the subject.

#### Editing subjects

To change the subject type and name expand the subject header if it's not already expanded. The subject type can be changed by means of the "Subject type" dropdown.

```{image} screenshots/editing_subject.png
:alt: Screenshot of dialog to edit a subject showing fields for the subject type, subject title, subject subtitle and comments
:class: only-light
```

```{image} screenshots/editing_subject_dark.png
:alt: Screenshot of dialog to edit a subject showing fields for the subject type, subject title, subject subtitle and comments
:class: only-dark
```

```{note}
Currently, changing the type of the subject does not affect what you can do with the subject.
```

To change the title or subtitle of the subject, enter a new title and/or subtitle in their respective fields.

The "{index}`Comment <pair: Comment;Subject>`" field can be used to describe the subject, or any other information. HTML and URLs are supported. The entered comments are shown between the subject title and the table with metrics.

#### Deleting subjects

To delete a subject expand the subject header and click the "Delete subject" button. The subject and all its metrics is deleted.

```{danger}
Be careful, there's no way to undo your action via the user interface.
```

#### Reordering subjects

To reorder subjects, expand the subject title and use the buttons on the lower left-hand side to move the subject up or down, or to the first or last position in the report. The order is saved on the server.

```{index} Metric
```

### Configuring metrics

#### Adding metrics

```{image} screenshots/adding_metric.png
:alt: Screenshot of buttons to add, copy, and move metrics
:class: only-light
```

```{image} screenshots/adding_metric_dark.png
:alt: Screenshot of buttons to add, copy, and move metrics
:class: only-dark
```

To add a metric to a subject, hit the "Add metric" button to select a metric type and create a new metric. Only metric types that can measure the subject are listed.

```{seealso}
See the [reference manual](reference.md) for the list of supported metric types.
```

*Quality-time* adds the selected metric to the report that you can next configure. It is immediately displayed in the metric table (and in the report dashboard) as white and with a question mark because *Quality-time* has no data on this metric yet.

Alternatively, you can also copy an existing metric or move an existing metric to the subject. Clicking the "Copy metric" or "Move metric" button shows a drop down menu with all of the metrics to choose from. Copying or moving a metric also copies or moves the sources of the metric.

#### Editing metrics

After you've added a metric, the metric is visible in the subject's metric table. You can change the metric configuration in the metric tab.

```{image} screenshots/editing_metric_configuration.png
:alt: Screenshot of tab to edit metrics showing fields for metric type, metric name, tags, metric scale, metric direction, metric unit, and metric targets
:class: only-light
```

```{image} screenshots/editing_metric_configuration_dark.png
:alt: Screenshot of tab to edit metrics showing fields for metric type, metric name, tags, metric scale, metric direction, metric unit, and metric targets
:class: only-dark
```

The first parameter is the "Metric type". The metric type determines what gets measured. By default, the name of the metric is equal to its type, "Accessibility violations" in the example above, but you can change the metric name using the "Metric name" field. When you change the metric type, the sources you can select in the "Sources" tab change accordingly.

```{warning}
If you change the type of a metric that has sources configured, sources that do not support the new metric type will be removed.
```

Metrics can have zero or more arbitrary "{index}`Tags <Tag>`". Most metric have a default tag, but you can remove it and/or add more if you like. For each tag, the report dashboard at the top of the page shows a summary of the metrics with that tag:

```{image} screenshots/dashboard_tags.png
:alt: Screenshot of dashboard cards showing pie charts for different tags
:class: only-light
```

```{image} screenshots/dashboard_tags_dark.png
:alt: Screenshot of dashboard cards showing pie charts for different tags
:class: only-dark
```

The "Metric {index}`scale <Scale>`" field determines what scale to use to measure the metric. Most metrics support either the "Count" scale, the "Percentage" scale, or both. In the example of the duplicated lines metric above, setting the metric scale to "Percentage" means that the percentage of lines that are duplicated is shown instead of the count of duplicated lines.

The "Metric {index}`direction <Direction>`" determines whether lower measurement values are considered to be better or worse. Usually, the default direction is correct. An example of a metric where you might want to change the direction is the "tests" metric. When used to measure the number of tests, more tests is better. But, when used to measure the number of failing tests, fewer is better.

The "Metric {index}`unit <Unit>`" derives its default value from the metric type. Override as needed.

The "Metric {index}`target <Target>`" determines at what value a measurement is below or above target. In the example below only measurement values of 0 are on target. The "Metric near target" determines when the measurement value is sufficiently close to the target to no longer require immediate action. Metrics near their target are yellow.

If you don't want to evaluate the metric against targets, but only want to track its measurement value, you can set the "Evaluate metric targets?" field to "No". The metric status will always be "Informative", unless the source data is missing.

```{index} Technical debt
```

#### Managing technical debt

If a metric doesn't meet the target value, but your team isn't able to fix the situation in the short run, you can accept the deviation as *{index}`technical debt <Technical debt>`*.

```{image} screenshots/editing_metric_technical_debt.png
:alt: Screenshot of tab to manage technical debt showing fields for technical debt, issues, and comments
:class: only-light
```

```{image} screenshots/editing_metric_technical_debt_dark.png
:alt: Screenshot of tab to manage technical debt showing fields for technical debt, issues, and comments
:class: only-dark
```

To accept technical debt, navigate to the "Technical debt" tab of the metric and set the "Accept technical debt?" field to "Yes". Enter the value you're accepting for the time being in the "Metric debt target" field. If you want to pay off the debt before a certain date, this can be registered in the "Technical debt end date" field.

The "{index}`Issue identifiers`" field can be used to enter the identifier of one or more issues in an issue tracker system. This can be used to track progress on resolving technical debt. See the [Issue tracker](#issue-tracker) section below on how to configure the issue tracker.

The "Create new issue" button can be used to create a new issue in the configured issue tracker. *Quality-time* will use the issue tracker's API to create a new issue and will add the new issue's id to the tracked issue identifiers. The created issue is opened in a new browser tab for further editing. You may have to allow *Quality-time* to open popup windows in your browser.

```{note}
Metrics with accepted technical debt are displayed with a money icon and grey background as long as their measurement value is worse than their target and equal to or better than their technical debt target.

However, measurement values of a metric with accepted technical debt will *not* be evaluated against the technical debt target when:

- the metric has a technical debt end date that is in the past, or
- the metric has issues associated with it, and the issue tracker reports that all these issues have been resolved.

If any of these situations apply, the technical debt target is ignored and the measurement value is evaluated against the target values. Depending on the evaluation, the metric is shown as green, yellow, or red, as usual.

Also, when the technical debt target is ignored, the target value is shown with a grey background in the target column and has a popup explaining *why* the accepted technical debt target is being ignored.
```

The "{index}`Comment <pair: Comment;Metric>`" field can be used to capture the rationale for accepting technical debt, or any other information. HTML and URLs are supported.

#### Reordering metrics

To reorder metrics, expand the metric in the metric table and use the buttons on the lower left-hand side to move the metric one row higher or lower, or to the top or bottom of the table. The order is saved on the server. You can temporarily override the default ordering of the metrics by clicking a column headers to sort the metrics by the values in that column.

#### Deleting metrics

To delete a metric, expand the metric in the metric table and click the "Delete metric" button. The metric and its sources are deleted.

```{danger}
Be careful, there's no way to undo your action via the user interface.
```

```{index} Source
```

### Configuring sources

#### Adding sources

```{image} screenshots/adding_source.png
:alt: Screenshot of buttons to add, copy, and move sources
:class: only-light
```

```{image} screenshots/adding_source_dark.png
:alt: Screenshot of buttons to add, copy, and move sources
:class: only-dark
```

To add a source to a metric, expand the metric in the metric table and then click the "Sources" tab. In the "Sources" tab, click the "Add source" button and select a source type. Only sources that can support the metric type are listed.

```{seealso}
See the [reference manual](reference.md) for the list of supported source types.
```

Alternatively, you can also copy an existing source or move an existing source to the metric. Clicking the "Copy source" or "Move source" button shows a drop down menu with all of the sources to choose from.

If you add multiple sources for one metric the measurement values of each source are combined to get one measurement value for the metric. Usually this means adding up the values, but for some metrics this doesn't make sense and the minimum or maximum value of the sources is used as the metric value.

#### Editing sources

After you've added a source, you can change the source type using the "Source type" drop-down menu. The available source types depend on the metric type. E.g. OWASP Dependency Check supports the security warnings metric type, but GitLab does not so GitLab is not shown.

By default, the name of the source equals the source type but this can be overridden using the "Source name" field.

The parameters that sources need differ per source type. Most sources need a URL, and optionally take either a username and password or a token so that *Quality-time* can access the source. If a parameter is required, this is indicated with a red outline as shown below.

```{image} screenshots/editing_source.png
:alt: Screenshot of dialog to edit source showing fields for the source type, source name, and source parameters such as URL and credentials
:class: only-light
```

```{image} screenshots/editing_source_dark.png
:alt: Screenshot of dialog to edit source showing fields for the source type, source name, and source parameters such as URL and credentials
:class: only-dark
```

Source parameter (URLs, usernames, passwords, etc.) changes can be applied to different scopes: to just the source being edited or to multiple sources that have the same type and value as the one being edited. When applying the change to multiple sources, the user can change all sources that have the same type and value of a metric, of a subject, of a report, or of all reports.

#### Deleting sources

To delete the source of a metric, first expand the metric in the metric table. Then, select the "Sources" tab and click the "Delete source" button. The source is deleted and no longer used to measure the metric.

```{danger}
Be careful, there's no way to undo your action via the user interface.
```

#### Reordering sources

To reorder sources, expand the metric in the metric table and click the sources tab. Use the buttons on the lower left-hand side of each source to move the source up or down, or to the top or bottom of the list of sources. The order is saved on the server.

```{index} Entity
```

### Configuring entities

An entity is a measured entity like for example one single failed job in GitLab for a metric that measures failed GitLab jobs or a single violation in SonarQube for a metric that measures violations. What exactly an entity is, and what properties it has depends on what the metric in question is measuring. Not every metric will have entities.

To add a source to a metric, expand the metric in the metric table and then click the tab with the source name. It will show a list of entities with all its details.

When clicking on one of the entities, it can be expanded and edited. Options are for example mark an entity as false positive or as fixed. Every action can be enriched with a comment for explanation.

## Customizing quality reports

You can customize quality reports by changing the dashboard layout, by changing the desired metric reaction times, by filtering metrics, and by filtering metric entities.

```{note}
Settings that you change via the 'Settings' panel are not shared with other users.
```

```{index} Dashboard
```

### Customizing dashboards

Both the reports dashboard on the *Quality-time* landing page and the dashboard of individual projects can be customized by dragging and dropping the cards.

The dashboard layout is persisted in the database and thus shared with other users.

```{index} Reaction time
```

### Desired reaction times

The default desired metric reaction times can be changed via the report's title. Expand the title and navigate to the 'Desired reaction times' tab. Each of the metric states that require action - target not met (red), near target (yellow), and status unknown (white) - has a desired reaction time in days that can be changed.

For each metric that requires action, *Quality-time* shows the time left to respond in the time left column. When the deadline is missed, the time left column shows '0 days' with a red background. Hovering over the time left value shows the deadline.

Metrics with accepted technical debt don't have a default desired reaction time. If a metric has accepted technical debt with an explicit end date though, that date will be used to show how much time is left in the metrics table.

When showing multiple dates in the metric table (this can be done via the Settings panel), *Quality-time* shows an 'overrun' column with the number of days that the metric deadline was missed in the displayed period. The purpose of this information is to gain an understanding of how well the team is responding to metrics that require action.

```{index} Trend table
```

### Measurement trend

By default, subjects show the current measurement value of each metric, together with other details such as the target value, comments and tags. Subjects can also list multiple recent measurement values of each metric to show the measurement trend. Use the 'Settings' panel in the menu bar to increase the number of dates displayed. The 'Settings' panel can also be used to configure the number of days or weeks between dates.

### Sorting metrics

Metrics can be sorted by clicking on the table column headers. The sort order cycles between the default order, sorted ascending by the column click, and sorted descending by the column clicked. The sort order can also be changed via the 'Settings' panel in the menu bar.

```{index} Tag
```

### Filtering metrics by tag

In a report's dashboard, click on a tag card to show only metrics that have the selected tag. The selected tag turns blue to indicate it is filtered on. Click the selected tag again to turn off the filtering. Selecting multiple tags shows metrics that have at least one of the selected tags.

### Filtering metrics by status

The 'Settings' panel in the menu bar can be used to hide metrics that need no action.

### Hiding columns

The 'Settings' panel in the menu bar can be used to hide specific columns from the metric tables.

```{index} Export report
```

```{index} PDF
```

## Export reports as PDF

*Quality-time* reports can be downloaded as PDF. To create PDFs, *Quality-time* has a rendering service included to convert the HTML report into PDF.

As *Quality-time* has to open the report in a (headless) browser and load all the metrics, creating the PDF can take some time. Especially for big reports.

```{tip}
The report title in the footer of the PDF will link to the online version of the same report.
```

### Manually

To manually download a PDF version of a report, navigate to the report and expand the report's title. Click the "Download report as PDF" button to create and download the PDF report.

The exported PDF report has the same metric table rows and columns hidden as in the user interface, and has the same metrics expanded as in the user interface. The exported PDF report also has the same date as the report visible in the user interface.

### Via the API

If the PDF report needs to be downloaded programmatically, e.g. for inclusion in a release package, use the API: `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf`. No authorization is needed for this API.

The `report_uuid` is the unique identifier that *Quality-time* assigns to a report. It can be found by navigating to a report in the browser and looking for the `report_uuid` in the address bar. For example, when the URL in the browser's address bar is `https://www.quality-time.example.org/f1d0e056-2440-43bd-b640-f6753ccf4496?hidden_columns=comment`, the part between the last slash and the question mark is the `report_uuid`.

To hide metrics that do not need any action, set the `hide_metrics_not_requiring_action` parameter to true, i.e. `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?hide_metrics_not_requiring_action=true`.

To hide columns from the report, set the `hidden_columns` parameter, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?hidden_columns=target,comment`. Possible options are `trend`, `status`, `measurement`, `target`, `source`, `comment`, `issues`, and `tags`.

To expand metrics and set the active tab of the metric detail information, add the `tabs` parameter, i.e. `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?tabs=<metric_uuid>:<tab_index>,<metric_uuid>:<tab_index>,...`. The metric UUID can be found by navigating to a report in the browser, expanding the metric, and looking for the `tabs` parameter in the address bar. For example, when the URL in the browser's address bar is `https://www.quality-time.example.org/1d0e056-2440-43bd-b640-f6753ccf4496?tabs=d4c0dea1-b072-417f-804e-6045544748db:0`, the part between the equal sign and the colon is the metric UUID of the expanded metric. The number after the colon is the number of the active tab, e.g. 0 is the metrics configuration tab, 1 is the source configuration tab, 2 is the trend graph, etc.

To show the measurement trend, add the `nr_dates` parameter and set it to more than 1, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?nr_dates=5`. The maximum supported value is 7 dates.

To change the time between dates shown, use the `date_interval` parameter. The interval should be an integer and can have the value 1, 7, 14, 21, or 28. For example, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?date_interval=7`.

To add issue attributes to the exported report, set the `show_issue_summary`, `show_issue_creation_date`, and/or `show_issue_update_date` parameters to `true`. For example, `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?show_issue_summary=true`.

To export an older version of a report, add the `report_date` parameter with a date value in ISO-format (YYYY-MM-DD), for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?report_date=2020-09-01`.

Reports contain the report URL in the footer of the report. When exporting PDFs manually, the *Quality-time* frontend supplies the report URL to the API. When using the API directly to export a report to PDF, the report URL needs to be supplied as parameter. Add the `report_url` parameter with the URL of the report, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?report_url=https://www.quality-time.example.org/<report_uuid>`.

```{index} Export report
```

```{index} Import report
```

## Export and import reports as JSON

*Quality-time* provides functionality for importing and exporting reports in JSON format. This functionality can be used for backing up reports or for transferring reports from one *Quality-time* instance to another one. Currently, this functionality is only available via the API, with one endpoint for importing and one for exporting the JSON reports.

A *Quality-time* report in JSON format contains the latest configuration of the report, with all its subjects, metrics and sources. It does not contain any actual measurements. The credentials of configured sources are encrypted on export to protect sensitive data.

To use the import and export endpoints you need to be authenticated. For example, using curl:

```console
curl --cookie-jar cookie.txt --request POST --header "Content-Type: application/json" --data '{"username": "jadoe", "password": "secret"}' https://quality-time.example.org/api/v3/login
```

### Exporting reports

The exporting endpoint is available via `https://quality-time.source.org/api/v3/report/<report-uuid>/json?public_key=<public-key>`. The exporting endpoint returns JSON content only.

For example, using curl, and assuming you have logged in as shown above:

```console
curl --cookie cookie.txt --output report.json https://quality-time.source.org/api/v3/report/97b2f341-45ce-4f2b-9a71-3675f2f54cf7/json
```

The `report_uuid` is the unique identifier that *Quality-time* assigns to a report. It can be found by navigating to a report in the browser and looking for the `report_uuid` in the address bar. For example, when the URL in the browser's address bar is `https://quality-time.source.org/f1d0e056-2440-43bd-b640-f6753ccf4496?hidden_columns=comment`, the part between the last slash and the question mark is the `report_uuid`.

The {index}`public key <Public key>` argument is optional. If no public key is provided, the public key of the exporting *Quality-time* instance is used for encrypting the source credentials. If the report needs to be imported in a different *Quality-time* instance, the public key of that instance should be provided. It can be obtained at `https://quality-time.destination.org/api/v3/public_key`. The exported JSON report can only be imported into the *Quality-time* whose public key has been used for the encryption of credentials during the export.

The public key endpoint returns a JSON like this:

```json
{
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAtXvAeTqsgXIb98rGfZDk\n4ZUssjjrMOCOL7xuZh6lYwN41UP0Day78tbzMxCx8mLfT76DckK1xkeGkKpS/UYD\n2ooDXluplRDGxfebZg+qy54toW878rnYe4HJu6YoDaBnthr1Muy9ttHOVB+6ucXY\nX23uzOF6FD4rZZTn4uGpEF9qfpzaVZrSpqWy9YAfZEsNNjqmbPYR+H0WjdihIpgY\n3AabLHdw02VN8cIzgh1ILLPFcBo2CqNWpETNIGdlPORfDiUx6HVxSXt80xwxFpop\n9hXQDuKSDVGlpVl5YKTwRyqEcFvhbTEJ1gJ+FksCRfrZ/hdVlI5mlCyN/gi+k3gO\nErtN0kFlIwCPyLHw5hsi/f8rLGpG1MaXmtI4fBoTbnozwaTcmoO9GO/Ell3ITTBW\nJbS3fSqKDtTU3NhalnJk5h99yQc+tgHIc+y/odKcicTDw5ZvlNIsY/ig6Z1BqYOl\n3FEI9a+I/mhcynSM/30elGsi+j/ZrWyhD6uB3E9+UtL5l7FtDWyIIoE7DaMQJZxg\nDNLCHWKACjjE+Tjr4ExUEgtzcMMmRXL2QZkylxxT9WU0Qe0U3nwJWBj6h+3xJird\npJ3weRfCPwrZ/6SxWE19tmZiynNnvnywxTJKgT15/Qkv1T0QyVCH/UeyxAhAXqYc\nBulld6J57dZwlpfWtf/ua3cCAwEAAQ==\n-----END PUBLIC KEY-----\n"
}
```

To be able to pass the public key as query parameter to the export endpoint, it needs to be encoded. Download the public key as file:

```console
curl --output public_key.json https://quality-time.destination.org/api/v3/public_key
```

And then encode the public key as follows:

```console
$ python3 -c 'import json; import urllib.parse; key = json.load(open("public_key.json"))["public_key"]; print(urllib.parse.quote_plus(key))'
-----BEGIN+PUBLIC+KEY----- ... encoded public key ... -----END+PUBLIC+KEY-----%0A
```

### Importing reports

The importing endpoint is available via `https://quality-time.destination.org/api/v3/report/import`. The import endpoint accepts JSON content only. See the [example reports](https://github.com/ICTU/quality-time/tree/master/components/shared_server_code/src/shared/example-reports) for the format.

For example, using curl, and assuming you have logged in as shown above:

```console
$ curl --cookie cookie.txt --request POST --header "Content-Type: application/json" --data @report.json https://quality-time.destination.org/api/v3/report/import
{"ok": true, "new_report_uuid": "97a3e341-44ce-4f2b-4471-36e5f2f34cf6"}
```

On import, all UUIDs contained in the report (UUIDs of the report, subjects, metrics and sources) will be replaced to prevent conflicts if the report already exists.

If the report contains encrypted credentials, the importing *Quality-time* instance will decrypt the credentials using its public key. Note that if the credentials were encrypted using the public key of a different *Quality-time* instance, an error will occur, and the import will fail.

To allow for seeding a *Quality-time* instance with default reports, imported reports may contain unencrypted credentials. These unencrypted credentials will be imported unchanged.

### Copying reports from one *Quality-time* instance to another

Tying the previous two sections together, these steps export a report from a source *Quality-time* instance and import it into a destination instance:

```console
# Get the public key of the destination Quality-time
$ curl --output public_key.json https://quality-time.destination.org/api/v3/public_key
# Encode the public key
$ python3 -c 'import json; import urllib.parse; key = json.load(open("public_key.json"))["public_key"]; print(urllib.parse.quote_plus(key))'
-----BEGIN+PUBLIC+KEY-----encoded-public-key-----END+PUBLIC+KEY-----%0A
# Log in to the source Quality-time
$ curl --cookie-jar cookie.txt --request POST --header "Content-Type: application/json" --data '{"username": "jadoe", "password": "secret"}' https://quality-time.source.org/api/v3/login
# Copy the public key and use it in the next line to export the report
$ curl --cookie cookie.txt --output report.json https://quality-time.source.org/api/v3/report/1352450b-30fa-4a82-aec5-7b5d0017ee13/json?public_key=-----BEGIN+PUBLIC+KEY-----encoded-public-key-----END+PUBLIC+KEY-----%0A
# Log in to the destination Quality-time
$ curl --cookie-jar cookie.txt --request POST --header "Content-Type: application/json" --data '{"username": "jadoe", "password": "secret"}' https://quality-time.destination.org/api/v3/login
# Import the report in the destination Quality-time
$ curl --cookie cookie.txt --request POST --header "Content-Type: application/json" --data @report.json https://quality-time.destination.org/api/v3/report/import
```

```{index} Issue tracker
```

## Issue tracker

To track work being done on metrics, for example to resolve technical debt, it's possible to add (identifiers of) issues to metrics. *Quality-time* uses these issue identifiers to check the status of the issue with an issue tracker. For this to work, an issue tracker needs to be added to the report. Expand the report header and configure the issue tracker in the issue tracker tab. Currently, only Jira can be used as issue tracker. Please consider submitting a pull request if you need support for other issue trackers such as Azure DevOps Server or GitLab.

Multiple issues can be linked to one metric. At most one issue tracker can be configured per report.

```{index} DORA metrics
```

## DORA metrics

DORA metrics are a set of four key metrics for measuring the performance of software delivery, first described by the DevOps Research & Assessment (DORA) team in the 2016 State of DevOps report. See the [DORA research program](https://www.devops-research.com/research.html) for more information.

*Quality-time* can monitor these metrics in the following manner:

- Deployment Frequency: measure "Job runs within time period" filtered on deployment jobs
- Lead Time for Changes: measure "Average issue lead time" filtered on issues marked as change
- Time to Restore Services: measure "Average issue lead time" filtered on issues marked as failure
- Change Failure Rate: measure "Issues" filtered on issues marked as failure in production

```{index} Notification
```

## Notifications

*Quality-time* can send notifications about metrics that change status to {index}`Microsoft Teams` channels. To enable notifications for a report, expand the report header and paste a [Microsoft Teams webhook](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook).

If a {index}`webhook <Webhook>` has been configured, *Quality-time* will check for changes in the status of metrics every minute. As soon as one or more metrics in the report change status, a notification will be sent to the Microsoft Teams channel configured by the webhook.
