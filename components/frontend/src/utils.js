import { arrayOf, number, objectOf, oneOf, string } from "prop-types"

import { PERMISSIONS } from "./context/Permissions"
import { defaultDesiredResponseTimes } from "./defaults"
import { STATUSES_NOT_REQUIRING_ACTION } from "./metric/status"
import {
    metricPropType,
    metricsPropType,
    metricsToHidePropType,
    reportPropType,
    reportsPropType,
    scalePropType,
    stringsPropType,
    subjectTypePropType,
} from "./sharedPropTypes"

export const MILLISECONDS_PER_HOUR = 60 * 60 * 1000
const MILLISECONDS_PER_DAY = 24 * MILLISECONDS_PER_HOUR

export const ISSUE_STATUS_COLORS = { todo: "grey", doing: "blue", done: "green", unknown: null }

export function getMetricDirection(metric, dataModel) {
    // Old versions of the data model may contain the unicode version of the direction, be prepared:
    return { "≦": "<", "≧": ">", "<": "<", ">": ">" }[metric.direction || dataModel.metrics[metric.type].direction]
}

export function formatMetricDirection(metric, dataModel) {
    return { "<": "≦", ">": "≧" }[getMetricDirection(metric, dataModel)]
}

export function getMetricName(metric, dataModel) {
    return metric.name || dataModel.metrics[metric.type].name
}

export function getSourceName(source, dataModel) {
    return source.name || dataModel.sources[source.type].name
}

function allMetrics(subject) {
    // Return all metrics of the subject, recursively
    const metrics = [...(subject.metrics ?? [])]
    Object.values(subject.subjects ?? {}).forEach((childSubject) => metrics.push(...allMetrics(childSubject)))
    return metrics
}

export function getSubjectTypeMetrics(subjectTypeKey, subjects) {
    // Return the metric types supported by the specified subject type
    const metrics = []
    Object.entries(subjects ?? {}).forEach(([key, subject]) => {
        if (key === subjectTypeKey) {
            metrics.push(...allMetrics(subject))
        } else {
            metrics.push(...getSubjectTypeMetrics(subjectTypeKey, subject.subjects))
        }
    })
    return Array.from(new Set(metrics))
}
getSubjectTypeMetrics.propTypes = {
    subjectTypeKey: string,
    subjects: objectOf(subjectTypePropType),
}

function childSubjects(subjects) {
    return Object.values(subjects).filter((subject) => !!subject.subjects)
}
childSubjects.propTypes = {
    subjects: objectOf(subjectTypePropType),
}

export function getSubjectType(subjectTypeKey, subjects) {
    // Return the subject type object
    if (Object.keys(subjects).includes(subjectTypeKey)) {
        return subjects[subjectTypeKey]
    }
    for (const childSubject of childSubjects(subjects)) {
        const result = getSubjectType(subjectTypeKey, childSubject.subjects)
        if (result) {
            return result
        }
    }
}
getSubjectType.propTypes = {
    subjectTypeKey: string,
    subjects: objectOf(subjectTypePropType),
}

export function getSubjectName(subject, dataModel) {
    return subject.name || getSubjectType(subject.type, dataModel.subjects).name
}

export function getMetricTarget(metric) {
    return metric.target || "0"
}

export function getMetricUnit(metric, dataModel) {
    return metric.unit || dataModel.metrics[metric.type].unit || ""
}

export function isMeasurementRequested(metric) {
    if (metric.measurement_requested) {
        if (metric.latest_measurement) {
            return new Date(metric.measurement_requested) >= new Date(metric.latest_measurement.end)
        }
        return true
    }
    return false
}

export function getMetricResponseDeadline(metric, report) {
    let deadline = null
    const status = metric.status || "unknown"
    if (status === "debt_target_met") {
        if (metric.debt_end_date) {
            deadline = new Date(metric.debt_end_date)
        }
    } else if (status in defaultDesiredResponseTimes && metric.status_start) {
        const desiredResponseTime = getDesiredResponseTime(report, status)
        if (Number.isInteger(desiredResponseTime)) {
            deadline = new Date(metric.status_start)
            deadline.setDate(deadline.getDate() + getDesiredResponseTime(report, status))
        }
    }
    return deadline
}

export function getMetricResponseTimeLeft(metric, report) {
    const deadline = getMetricResponseDeadline(metric, report)
    const now = new Date()
    return deadline === null ? null : deadline.getTime() - now.getTime()
}

function getMetricResponseOverruns(metric_uuid, metric, measurements, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    let previousStatus
    const consolidatedMeasurements = []
    const filteredMeasurements = measurements.filter((measurement) => measurement.metric_uuid === metric_uuid)
    filteredMeasurements.forEach((measurement) => {
        const status = measurement?.[scale]?.status || "unknown"
        if (status === previousStatus) {
            consolidatedMeasurements.at(-1).end = measurement.end // Status unchanged so merge this measurement with the previous one
        } else {
            consolidatedMeasurements.push(measurement) // Status changed or first one, so keep this measurement
        }
        previousStatus = status
    })
    return consolidatedMeasurements
}

export function getMetricResponseOverrun(metric_uuid, metric, report, measurements, dataModel) {
    const consolidatedMeasurements = getMetricResponseOverruns(metric_uuid, metric, measurements, dataModel)
    const scale = getMetricScale(metric, dataModel)
    let totalOverrun = 0 // Amount of time the desired response time was not achieved for this metric
    const overruns = []
    consolidatedMeasurements.forEach((measurement) => {
        const status = measurement?.[scale]?.status || "unknown"
        if (status in defaultDesiredResponseTimes) {
            let desiredResponseTime = getDesiredResponseTime(report, status)
            if (Number.isInteger(desiredResponseTime)) {
                desiredResponseTime *= MILLISECONDS_PER_DAY
                const actualResponseTime = new Date(measurement.end).getTime() - new Date(measurement.start).getTime()
                const overrun = Math.max(0, actualResponseTime - desiredResponseTime)
                if (overrun > 0) {
                    overruns.push({
                        status: status,
                        start: measurement.start,
                        end: measurement.end,
                        desired_response_time: days(desiredResponseTime),
                        actual_response_time: days(actualResponseTime),
                        overrun: days(overrun),
                    })
                    totalOverrun += overrun
                }
            }
        }
    })
    return { totalOverrun: days(totalOverrun), overruns: overruns }
}

export function getDesiredResponseTime(report, status) {
    // Precondition: status is a key of defaultDesiredResponseTimes
    const desiredResponseTime = report?.desired_response_times?.[status]
    if (desiredResponseTime === undefined) {
        return defaultDesiredResponseTimes[status]
    }
    return desiredResponseTime === null ? null : Number.parseInt(desiredResponseTime)
}

export function getMetricValue(metric, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    return metric?.latest_measurement?.[scale]?.value ?? ""
}

export function getMetricComment(metric) {
    return metric.comment ?? ""
}

export function getMetricScale(metric, dataModel) {
    return metric.scale || dataModel.metrics[metric.type].default_scale || "count"
}

export function getMetricStatus(metric) {
    return metric.status ?? "unknown"
}

export function getMetricTags(metric) {
    const tags = metric.tags ?? []
    sortWithLocaleCompare(tags)
    return tags
}
getMetricTags.propTypes = {
    metric: metricPropType,
}

export function sortWithLocaleCompare(strings) {
    strings.sort((string1, string2) => string1.localeCompare(string2))
}
sortWithLocaleCompare.propTypes = {
    strings: stringsPropType,
}

function hideMetric(metric, metricsToHide, hiddenTags) {
    const hideBecauseNoActionNeeded =
        metricsToHide === "no_action_required" && STATUSES_NOT_REQUIRING_ACTION.includes(metric.status)
    const hideBecauseNoIssues = metricsToHide === "no_issues" && !metric?.issue_ids?.length
    const hideBecauseTagIsHidden =
        hiddenTags?.length > 0 &&
        hiddenTags?.filter((hiddenTag) => metric.tags?.includes(hiddenTag)).length >= metric.tags?.length
    return hideBecauseNoActionNeeded || hideBecauseNoIssues || hideBecauseTagIsHidden
}
hideMetric.propTypes = {
    metric: metricPropType,
    metricsToHide: metricsToHidePropType,
    hiddenTags: stringsPropType,
}

export function visibleMetrics(metrics, metricsToHide, hiddenTags) {
    if (metricsToHide === "all") {
        return {}
    }
    return Object.fromEntries(
        Object.entries(metrics).filter(([_, metric]) => !hideMetric(metric, metricsToHide, hiddenTags)),
    )
}
visibleMetrics.propTypes = {
    metrics: metricsPropType,
    metricsToHide: metricsToHidePropType,
    hiddenTags: stringsPropType,
}

export function getReportTags(report, hiddenTags) {
    const tags = new Set()
    Object.values(report.subjects).forEach((subject) => {
        Object.values(subject.metrics).forEach((metric) => {
            getMetricTags(metric).forEach((tag) => {
                if (!(hiddenTags ?? []).includes(tag)) {
                    tags.add(tag)
                }
            })
        })
    })
    const sortedTags = Array.from(tags)
    sortWithLocaleCompare(sortedTags)
    return sortedTags
}

export function getReportsTags(reports) {
    const tags = new Set()
    reports.forEach((report) => {
        getReportTags(report).forEach((tag) => tags.add(tag))
    })
    const sortedTags = Array.from(tags)
    sortWithLocaleCompare(sortedTags)
    return sortedTags
}

export function nrMetricsInReport(report) {
    let nrMetrics = 0
    Object.values(report.subjects).forEach((subject) => {
        nrMetrics += Object.keys(subject.metrics).length
    })
    return nrMetrics
}
nrMetricsInReport.propTypes = {
    report: reportPropType,
}

export function nrMetricsInReports(reports) {
    let nrMetrics = 0
    reports.forEach((report) => {
        nrMetrics += nrMetricsInReport(report)
    })
    return nrMetrics
}
nrMetricsInReport.propTypes = {
    reports: reportsPropType,
}

export function getMetricIssueIds(metric) {
    let issueIds = metric.issue_ids ?? []
    sortWithLocaleCompare(issueIds)
    return issueIds
}
getMetricIssueIds.propTypes = {
    metric: metricPropType,
}

export function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1).replaceAll("_", " ")
}

export function pluralize(word, count) {
    // Pluralize (naively; it doesn't work for words like sheep) the word if count > 1
    return word + (count === 1 ? "" : "s")
}

export function niceNumber(number) {
    let rounded_numbers = [10, 12, 15, 20, 30, 50, 75]
    do {
        for (let rounded_number of rounded_numbers) {
            if (number <= (9 * rounded_number) / 10) {
                return rounded_number
            }
        }
        rounded_numbers = rounded_numbers.map((value) => {
            return value * 10
        })
    } while (true) // eslint-disable-line no-constant-condition
}

export function scaledNumber(number) {
    const scale = ["", "k", "m"]
    const exponent = Math.floor(Math.log(number) / Math.log(1000))
    return (number / Math.pow(1000, exponent)).toFixed(0) + scale[exponent]
}

export function formatMetricValue(scale, value) {
    if (value === "?") {
        return value
    }
    if (scale === "count") {
        const number = Math.round(Number(value))
        return number.toLocaleString(undefined, { useGrouping: true })
    }
    return value
}
formatMetricValue.propTypes = {
    scale: scalePropType,
    value: string,
}

export function formatMetricScale(metric, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    return scale === "percentage" ? "%" : ""
}

export function formatMetricScaleAndUnit(metric, dataModel) {
    const scale = formatMetricScale(metric, dataModel)
    const unit = getMetricUnit(metric, dataModel)
    const sep = unit ? " " : ""
    return `${scale}${sep}${unit}`
}

export function days(timeInMs) {
    return Math.round(timeInMs / MILLISECONDS_PER_DAY)
}

export function isValidDate_YYYYMMDD(string) {
    if (/^\d{4}-\d{2}-\d{2}$/.test(string)) {
        const milliseconds_since_epoch = Date.parse(string)
        return !isNaN(milliseconds_since_epoch)
    }
    return false
}

export function toISODateStringInCurrentTZ(date) {
    // Return an ISO date string without changing the timezone to UTC as Date.toISOString does
    return `${String(date.getFullYear())}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`
}

export function getUserPermissions(username, email, report_date, permissions) {
    if (username === null || report_date !== null) {
        return []
    }
    return PERMISSIONS.filter((permission) => {
        const permittedUsers = permissions?.[permission] ?? []
        return permittedUsers.length === 0 ? true : permittedUsers.includes(username) || permittedUsers.includes(email)
    })
}

export function userPrefersDarkMode(uiMode) {
    return uiMode === "dark" || (uiMode === "system" && window.matchMedia?.("(prefers-color-scheme: dark)").matches)
}

export function dropdownOptions(options) {
    return options.map((option) => ({ key: option, text: option, value: option }))
}

export function slugify(name) {
    // The hash isn't really part of the slug, but to prevent duplication it is included anyway
    return `#${name?.toLowerCase().replaceAll(" ", "-").replaceAll("(", "").replaceAll(")", "").replaceAll("/", "")}`
}

export function addCounts(object1, object2) {
    // Assuming object1 and object2 are objects of the form {key1: count1, key2: count2, ...}, add them together
    if (JSON.stringify(Object.keys(object1)) !== JSON.stringify(Object.keys(object2))) {
        throw new Error("Can't add the counts of objects with different keys")
    }
    const result = {}
    Object.keys(object1).forEach((key) => {
        result[key] = object1[key] + object2[key]
    })
    return result
}

export function sum(object) {
    const list = typeof object == Array ? object : Object.values(object)
    return list.reduce((a, b) => a + b, 0)
}
sum.propTypes = {
    object: oneOf([arrayOf(number), objectOf(number)]),
}
