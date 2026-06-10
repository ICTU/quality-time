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
import {
    addCounts,
    getMetricName,
    getMetricScale,
    getMetricTags,
    getSourceLocationName,
    getSubjectName,
    visibleMetrics,
} from "../utils"

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
    for (const [metricUuid, metric] of Object.entries(metrics)) {
        if (!tag || getMetricTags(metric).includes(tag)) {
            const status = metricStatusOnDate(metricUuid, metric, measurements, date, dataModel)
            summary[STATUS_COLORS[status]] += 1
        }
    }
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
    for (const subject of Object.values(report.subjects)) {
        const metrics = visibleMetrics(subject.metrics, metricsToHide, settings.hiddenTags.value)
        summary = addCounts(summary, summarizeMetricsOnDate(dataModel, date, measurements, metrics, tag))
    }
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
    for (const report of reports) {
        summary = addCounts(summary, summarizeReportOnDate(dataModel, settings, report, measurements, date, tag))
    }
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

export function sortedSourceLocations(dataModel, report) {
    // Return the source locations of the report as a sorted list of [sourceLocationUuid, sourceLocation] pairs
    const sourceLocations = Object.entries(report.source_locations ?? {})
    sourceLocations.sort((location1, location2) =>
        getSourceLocationName(location1[1], dataModel).localeCompare(getSourceLocationName(location2[1], dataModel)),
    )
    return sourceLocations
}
sortedSourceLocations.propTypes = {
    dataModel: dataModelPropType,
    report: reportPropType,
}

export function sourcesUsingSourceLocation(report, sourceLocationUuid) {
    // Return the number of sources in the report that use the source location
    let nrSources = 0
    for (const { source } of iterateSources(report)) {
        if (source.source_location === sourceLocationUuid) {
            nrSources += 1
        }
    }
    return nrSources
}
sourcesUsingSourceLocation.propTypes = {
    report: reportPropType,
    sourceLocationUuid: string,
}

export function metricsUsingSourceLocation(dataModel, report, sourceLocationUuid) {
    // Return the metrics in the report that have a source that uses the source location
    const metrics = {}
    for (const { subject, subjectUuid, metric, metricUuid, source } of iterateSources(report)) {
        if (source.source_location === sourceLocationUuid) {
            metrics[metricUuid] = {
                name: getMetricName(metric, dataModel),
                secondary_name: metric.secondary_name ?? "",
                subjectName: getSubjectName(subject, dataModel),
                subjectUuid: subjectUuid,
            }
        }
    }
    return metrics
}
metricsUsingSourceLocation.propTypes = {
    dataModel: dataModelPropType,
    report: reportPropType,
    sourceLocationUuid: string,
}

export function unusedMetricTypesSupportedBySourceLocation(dataModel, report, sourceLocationUuid) {
    // Return the metric types that can be measured with the source location but aren't currently measured in the
    // report using the source location
    const sourceType = report.source_locations?.[sourceLocationUuid]?.source_type
    const supportedMetricTypes = new Set()
    for (const [metricType, metric] of Object.entries(dataModel.metrics)) {
        if (metric.sources.includes(sourceType)) {
            supportedMetricTypes.add(metricType)
        }
    }
    const usedMetricTypes = new Set()
    for (const { metric, source } of iterateSources(report)) {
        if (source.source_location === sourceLocationUuid) {
            usedMetricTypes.add(metric.type)
        }
    }
    return supportedMetricTypes.difference(usedMetricTypes)
}
unusedMetricTypesSupportedBySourceLocation.propTypes = {
    dataModel: dataModelPropType,
    report: reportPropType,
    sourceLocationUuid: string,
}

function iterateSources(report) {
    // Iterate over all sources in the report, also returning the containing subjects and metrics, and the uuids
    const items = []
    for (const [subjectUuid, subject] of Object.entries(report.subjects ?? {})) {
        for (const [metricUuid, metric] of Object.entries(subject.metrics ?? {})) {
            for (const [sourceUuid, source] of Object.entries(metric.sources ?? {})) {
                items.push({
                    subject: subject,
                    subjectUuid: subjectUuid,
                    metric: metric,
                    metricUuid: metricUuid,
                    source: source,
                    sourceUuid: sourceUuid,
                })
            }
        }
    }
    return items
}
