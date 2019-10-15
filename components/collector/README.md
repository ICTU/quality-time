# Quality-time collector

The collector is responsible for collecting measurement data from sources. It wakes up once every minute and asks the server for a list of all metrics. For each metric, the collector gets the measurement data from each of the metric's sources and posts a new measurement to the server.

If a metric has been recently measured and its parameters haven't been changed, the collector skips the metric.

