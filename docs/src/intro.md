# About *Quality-time*

*Quality-time* is an automated quality system for software development and maintenance. *Quality-time* collects measurement data from sources such as Gitlab, SonarQube, Jira, Azure DevOps, and OWASP Dependency Check, to provide an overview of the quality of software products and projects. It does so by comparing measurement data with metric targets and informing development teams about the metrics that need improvement actions.

Technically, *Quality-time* consists of a React frontend, a Mongo database server, and three backend components written in Python: an API-server, a worker component to collect measurement data from the sources, and a worker component to send notifications.

Users can add and configure reports, metrics, and sources (such as SonarQube and Jira) in the frontend. The collector collects metrics data from the configured metric sources. It posts the measurements to the server which in turn stores them in the database. The frontend calls the server to get the reports and the measurements and presents them to the user.

*Quality-time* is developed by [ICTU](https://ictu.nl/about-us), an independent consultancy and project organisation within the Dutch government, helping government organizations develop and implement digital services.

# Screenshots

Some screenshots to wet your appetite.

## Projects dashboard

*Quality-time* shows a summary of the projects on its landing page:

![Screenshot of a Quality-time dashboard with three demo projects in the form of donut charts](screenshots/projects_dashboard.png)

## Metrics overview

For each metric, *Quality-time* displays the key data:

![Screenshot of a demo app with metrics that have different statuses](screenshots/metrics.png)

## Metric details

Users can expand the metrics to see and configure the metric details:

![Screenshot of a metric source configuration form](screenshots/metric_details.png)

Keep track of trends:

![Screenshot of a metric trend graph showing the value of the metric over time](screenshots/metric_trendgraph.png)

And manage false positives:

![Screenshot of a metric's entities, in this case suppressed violations](screenshots/metric_entities.png)

# Features

Implemented features include:

- Robust data collection (the collector should never fail, even in the face of misconfigured or unavailable sources).
- Measurement history is kept in a database, allowing for time travel.
- Easy report configuration via the UI.
- Multiple reports in one *Quality-time* instance.
- LDAP-integration.
- Generic false-positive management.
- Metric tags can be used to summarize metrics with the same tag across subjects, e.g. to summarize all security metrics.
- Export of reports to PDF, both via the UI as well as via the API.
- Notifications of events, such as metrics turning red, to Microsoft Teams.
- Side-by-side comparison of measurements at different points in time.

For more plans, see the [issue tracker](https://github.com/ICTU/quality-time/issues).

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
