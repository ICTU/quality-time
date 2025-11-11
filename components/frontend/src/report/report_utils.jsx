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
    sourcePropType,
    sourceTypePropType,
} from "../sharedPropTypes"
import {
    addCounts,
    getMetricName,
    getMetricScale,
    getMetricTags,
    getSourceName,
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
        if (!tag || getMetricTags(metric).indexOf(tag) >= 0) {
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

export function reportSources(dataModel, report) {
    const sourceIds = new Set()
    const sources = {}
    for (const { source, sourceUuid } of iterateSources(report)) {
        const sourceId = createSourceId(dataModel, source)
        if (sourceIds.has(sourceId)) {
            sources[sourceId].nrMetrics += 1
        } else {
            source["uuid"] = sourceUuid
            source["nrMetrics"] = 1
            sources[sourceId] = source
            sourceIds.add(sourceId)
        }
    }
    const sortedSources = Object.values(sources)
    sortedSources.sort((s1, s2) => (s1.name || s1.type).localeCompare(s2.name || s2.type))
    return sortedSources
}
reportSources.propTypes = {
    dataModel: dataModelPropType,
    report: reportPropType,
}

export function metricsUsingSource(dataModel, report, source) {
    // Return the metrics in the report that use the source with the given sourceUuid or a source with the same
    // parameters
    const metrics = {}
    const sourceId = createSourceId(dataModel, source)
    for (const { subject, subjectUuid, metric, metricUuid, source } of iterateSources(report)) {
        if (createSourceId(dataModel, source) === sourceId) {
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
metricsUsingSource.propTypes = {
    dataModel: dataModelPropType,
    report: reportPropType,
    source: sourcePropType,
}

export function unusedMetricTypesSupportedBySource(dataModel, report, source) {
    // Return the metric types that can be measured with the source but aren't currently measured in the report
    const supportedMetricTypes = new Set()
    for (const [metricType, metric] of Object.entries(dataModel.metrics)) {
        if (metric.sources.includes(source.type)) {
            supportedMetricTypes.add(metricType)
        }
    }
    const usedMetricTypes = new Set()
    const sourceId = createSourceId(dataModel, source)
    for (const { metric, source } of iterateSources(report)) {
        if (createSourceId(dataModel, source) === sourceId) {
            usedMetricTypes.add(metric.type)
        }
    }
    return supportedMetricTypes.difference(usedMetricTypes)
}
unusedMetricTypesSupportedBySource.propTypes = {
    dataModel: dataModelPropType,
    report: reportPropType,
    source: sourceTypePropType,
}

function createSourceId(dataModel, source) {
    // Return the stringified version of the source. This creates a source identifier that makes
    // sources with the same location parameters equal and ignores the source uuid and parameters such as filters,
    const identifyingFields = {
        name: getSourceName(source, dataModel),
        type: source.type,
        url: source.parameters?.url ?? "",
        landing_url: source.parameters?.landing_url ?? "",
        username: source.parameters?.username ?? "",
        password: source.parameters?.password ?? "",
        private_token: source.parameters?.private_token ?? "",
        api_version: source.parameters?.api_version ?? "",
    }
    return JSON.stringify(identifyingFields)
}
createSourceId.propTypes = {
    dataModel: dataModelPropType,
    source: sourcePropType,
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
