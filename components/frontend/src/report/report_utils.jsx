import { string } from "prop-types"

import { STATUS_COLORS } from "../metric/status"
import {
    dataModelPropType,
    datePropType,
    measurementsPropType,
    metricPropType,
    metricsPropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
} from "../sharedPropTypes"
import { addCounts, getMetricScale, getMetricTags, visibleMetrics } from "../utils"

export function measurementOnDate(date, measurements, metricUuid) {
    const isoDateString = date.toISOString().split("T")[0]
    return measurements?.find((m) => {
        return (
            m.metric_uuid === metricUuid &&
            m.start.split("T")[0] <= isoDateString &&
            isoDateString <= m.end.split("T")[0]
        )
    })
}
measurementOnDate.propTypes = {
    date: datePropType,
    measurements: measurementsPropType,
    metricUuid: string,
}

function metricStatusOnDate(metricUuid, metric, measurements, date, dataModel) {
    const measurement = measurementOnDate(date, measurements, metricUuid)
    const scale = getMetricScale(metric, dataModel)
    return measurement?.[scale]?.status ?? "unknown"
}
metricStatusOnDate.propTypes = {
    metricUuid: string,
    metric: metricPropType,
    measurements: measurementsPropType,
    date: datePropType,
    dataModel: dataModelPropType,
}

export function summarizeMetricsOnDate(dataModel, date, measurements, metrics, tag) {
    // Summarize the number of metrics per color on the given date, and filtered by tag, if specified
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.entries(metrics).forEach(([metricUuid, metric]) => {
        if (!tag || getMetricTags(metric).indexOf(tag) >= 0) {
            const status = metricStatusOnDate(metricUuid, metric, measurements, date, dataModel)
            summary[STATUS_COLORS[status]] += 1
        }
    })
    return summary
}
summarizeMetricsOnDate.propType = {
    dataModel: dataModelPropType,
    date: datePropType,
    measurements: measurementsPropType,
    metrics: metricsPropType,
    tag: string,
}

export function summarizeReportOnDate(dataModel, settings, report, measurements, date, tag) {
    // Summarize the number of metrics per color in the report on the given date, and filtered by tag, if specified
    let summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    const metricsToHide = settings.metricsToHide.value === "all" ? "none" : settings.metricsToHide.value
    Object.values(report.subjects).forEach((subject) => {
        const metrics = visibleMetrics(subject.metrics, metricsToHide, settings.hiddenTags.value)
        summary = addCounts(summary, summarizeMetricsOnDate(dataModel, date, measurements, metrics, tag))
    })
    return summary
}
summarizeReportOnDate.propTypes = {
    dataModel: dataModelPropType,
    date: datePropType,
    measurements: measurementsPropType,
    report: reportPropType,
    settings: settingsPropType,
    tag: string,
}

export function summarizeReportsOnDate(dataModel, settings, reports, measurements, date, tag) {
    // Summarize the number of metrics per color in the reports on the given date, and filtered by tag, if specified
    let summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    reports.forEach((report) => {
        summary = addCounts(summary, summarizeReportOnDate(dataModel, settings, report, measurements, date, tag))
    })
    return summary
}
summarizeReportsOnDate.propTypes = {
    dataModel: dataModelPropType,
    date: datePropType,
    measurements: measurementsPropType,
    reports: reportsPropType,
    settings: settingsPropType,
    tag: string,
}
