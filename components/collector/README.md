# *Quality-time* collector

## Overview

The collector is responsible for collecting measurement data from sources. It wakes up once every minute and asks the server for a list of all metrics. For each metric, the collector gets the measurement data from each of the metric's sources and posts a new measurement to the server.

If a metric has been recently measured and its parameters haven't been changed, the collector skips the metric.

## Health check

Every time the collector wakes up, it writes the current date and time in ISO format to the 'health_check.txt' file. This date and time is read by the Docker health check (see the [Dockerfile](Dockerfile)). If the written date and time are too long ago, the collector container is considered to be unhealthy.

## Configuration

The collector uses the following environment variables:

| Name | Default value | Description |
| :--- | :---------- | :------------ |
| SERVER_HOST | server | Hostname of the server. The collector uses this to get the metrics and post the measurements. |
| SERVER_PORT | 5001 | Port of the server. The collector uses this to get the metrics and post the measurements. |
| COLLECTOR_SLEEP_DURATION | 20 | The maximum amount of time (in seconds) that the collector sleeps between collecting measurements. |
| COLLECTOR_MEASUREMENT_LIMIT | 30 | The maximum number of metrics that the collector measures each time it wakes up. If more metrics need to be measured, they will be measured the next time the collector wakes up. |
| COLLECTOR_MEASUREMENT_FREQUENCY | 900 | The amount of time (in seconds) after which a metric should be measured again. |
