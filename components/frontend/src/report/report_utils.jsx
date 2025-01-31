import { STATUS_COLORS } from "../metric/status"
import { addCounts, getMetricScale, getMetricTags, visibleMetrics } from "../utils"

function metricStatusOnDate(metric_uuid, metric, measurements, date, dataModel) {
    const isoDateString = date.toISOString().split("T")[0]
    const measurement = measurements?.find((m) => {
        return (
            m.metric_uuid === metric_uuid &&
            m.start.split("T")[0] <= isoDateString &&
            isoDateString <= m.end.split("T")[0]
        )
    })
    const scale = getMetricScale(metric, dataModel)
    return measurement?.[scale]?.status ?? "unknown"
}

export function summarizeMetricsOnDate(dataModel, metrics, measurements, date, tag) {
    // Summarize the number of metrics per color on the given date, and filtered by tag, if specified
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.entries(metrics).forEach(([metric_uuid, metric]) => {
        if (!tag || getMetricTags(metric).indexOf(tag) >= 0) {
            const status = metricStatusOnDate(metric_uuid, metric, measurements, date, dataModel)
            summary[STATUS_COLORS[status]] += 1
        }
    })
    return summary
}

export function summarizeReportOnDate(dataModel, settings, report, measurements, date, tag) {
    // Summarize the number of metrics per color in the report on the given date, and filtered by tag, if specified
    let summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    const metricsToHide = settings.metricsToHide.value === "all" ? "none" : settings.metricsToHide.value
    Object.values(report.subjects).forEach((subject) => {
        const metrics = visibleMetrics(subject.metrics, metricsToHide, settings.hiddenTags.value)
        summary = addCounts(summary, summarizeMetricsOnDate(dataModel, metrics, measurements, date, tag))
    })
    return summary
}

export function summarizeReportsOnDate(dataModel, settings, reports, measurements, date, tag) {
    // Summarize the number of metrics per color in the reports on the given date, and filtered by tag, if specified
    let summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    reports.forEach((report) => {
        summary = addCounts(summary, summarizeReportOnDate(dataModel, settings, report, measurements, date, tag))
    })
    return summary
}
