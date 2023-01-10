# About *Quality-time*

*Quality-time* is an automated quality system for software development and maintenance. *Quality-time* collects measurement data from sources such as GitLab, SonarQube, Jira, Azure DevOps, and OWASP Dependency Check, to provide an overview of the quality of software products, processes, and projects. It does so by comparing measurement data with metric targets and informing development teams about the metrics that need improvement actions.

Technically, *Quality-time* consists of a React frontend, a Mongo database server, and a number of backend components written in Python: a worker component to collect measurement data from the sources, a worker component to send notifications, an API-server for the frontend, and an API-server for the worker components.

Users can add and configure reports, metrics, and sources (such as SonarQube and Jira) in the frontend. The collector collects metrics data from the configured metric sources. It posts the measurements to the server which in turn stores them in the database. The frontend calls the server to get the reports and the measurements and presents them to the user.

*Quality-time* is developed by [ICTU](https://www.ictu.nl/about-us), an independent consultancy and project organisation within the Dutch government, helping government organizations develop and implement digital services.

# Screenshots

Some screenshots to wet your appetite.

```{tip}
*Quality-time* supports both a light and a dark UI mode. Toggle the UI mode of the documentation, using the icon at the top of the page, to also toggle the UI mode of the screenshots.
```

## Projects dashboard

*Quality-time* shows a summary of the projects on its landing page:

```{image} screenshots/projects_dashboard_dark.png
:alt: Screenshot of a Quality-time dashboard with three demo projects in the form of donut charts
:class: only-dark
```

```{image} screenshots/projects_dashboard.png
:alt: Screenshot of a Quality-time dashboard with three demo projects in the form of donut charts
:class: only-light
```

## Metrics overview

For each metric, *Quality-time* displays the key data:

```{image} screenshots/metrics.png
:alt: Screenshot of a demo app with metrics that have different statuses
:class: only-light
```

```{image} screenshots/metrics_dark.png
:alt: Screenshot of a demo app with metrics that have different statuses
:class: only-dark
```

## Metric details

Users can expand the metrics to see and configure the metric details:

```{image} screenshots/metric_details.png
:alt: Screenshot of a metric source configuration form
:class: only-light
```

```{image} screenshots/metric_details_dark.png
:alt: Screenshot of a metric source configuration form
:class: only-dark
```

Keep track of trends:

```{image} screenshots/metric_trendgraph.png
:alt: Screenshot of a metric trend graph showing the value of the metric over time
:class: only-light
```

```{image} screenshots/metric_trendgraph_dark.png
:alt: Screenshot of a metric trend graph showing the value of the metric over time
:class: only-dark
```

And manage false positives:

```{image} screenshots/metric_entities.png
:alt: Screenshot of the entities of the metric, in this case suppressed violations
:class: only-light
```

```{image} screenshots/metric_entities_dark.png
:alt: Screenshot of the entities of the metric, in this case suppressed violations
:class: only-dark
```

# Features

Implemented features include:

- Robust data collection (the collector should never fail, even in the face of misconfigured or unavailable sources).
- Measurement history is kept in a database, allowing for time travel.
- Report configuration via the UI.
- Multiple reports in one *Quality-time* instance.
- LDAP-integration.
- Generic false-positive management.
- Metric tags can be used to summarize metrics with the same tag across subjects, e.g. to summarize all security metrics.
- Export of reports to PDF, both via the UI as well as via the API.
- Notifications of events, such as metrics turning red, to Microsoft Teams.
- Side-by-side comparison of measurements at different points in time.
- Integration with issue tracker (Jira only at the moment) to manage actions and technical debt.
- Dark and light UI mode.

```{seealso}
For more plans, see the [issue tracker](https://github.com/ICTU/quality-time/issues).
```

# Trying it out

*Quality-time* requires Docker and Docker-compose.

Clone this repository:

```console
git clone https://github.com/ICTU/quality-time.git
```

Build the containers:

```console
docker-compose build
```

Start the containers:

```console
docker-compose up
```

*Quality-time* is served at [http://localhost](http://localhost). Use username `jadoe` and password `secret` to log in.

# Why *Quality-time*?

ICTU developed *Quality-time* to help projects and teams within ICTU gain actionable insight into the quality of the software they are developing and maintaining. The current vision on the scope of *Quality-time* is:

- *Quality-time* collects data from sources that projects and teams are using anyway to develop and maintain software. Think version control systems, build tools, backlog management tools, test reports, security tools, and other quality tools. *Quality-time* does not analyse the software itself, but relies on information from these tools to create an integrated and actionable overview.
- The sources that *Quality-time* uses to collect its measurement data are automated. Manual sources for measurements are possible, but automated sources are preferred.
- *Quality-time* evaluates measurement data against target values. It shows users which metrics do not meet their target value, so users can take corrective action. *Informational* metrics, meaning metrics without target, are possible, but most metrics are assumed to have targets.
- *Quality-time* provides a single overview of the software measurements, but refers users to the underlying tools for detailed information.
- Technical debt management is an integral part of software quality management. Any metric that does not meet its target value for a longer period of time can be considered to represent a form of debt that needs to be managed.
- Tools come and go. Hence, an important non-functional requirement for *Quality-time* is the ability to quickly add interfacing to new sources.
- *Quality-time* provides actionable information on current quality issues and risks. Historical information is retained, but is a second-class citizen.
- *Quality-time* is not an issue tracker or task manager. It does integrate with issue trackers, however, making it easy to create issues for metrics that need action and to manage technical debt.
- Software quality is usually broken down into quality characteristics such as maintainability, testability, and accessibility, as for example in ISO 25010. Many metrics in *Quality-time* measure parts of these quality characteristics. For example, the number of 'code smells' and the 'complexity' of source code are both related to maintainability. However, *Quality-time* does not attempt to aggregate these metrics into a measurement of quality characteristics. Such aggregations typically lack a sound mathematical and scientific basis and are often not actionable.

```{note}
The name *Quality-time* is of course a call to action: spend more quality time with the software you develop 😁
```
