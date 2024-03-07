import { arrayOf, number, objectOf, oneOf, string } from 'prop-types'
import { PERMISSIONS } from './context/Permissions';
import { HyperLink } from './widgets/HyperLink';
import { defaultDesiredResponseTimes } from './defaults';
import { metricPropType, reportPropType, reportsPropType, stringsPropType } from './sharedPropTypes';

export const MILLISECONDS_PER_HOUR = 60 * 60 * 1000;
const MILLISECONDS_PER_DAY = 24 * MILLISECONDS_PER_HOUR;

export const STATUSES = ["unknown", "target_not_met", "near_target_met", "target_met", "debt_target_met", "informative"];
export const STATUS_COLORS = {
    informative: "blue",
    target_met: "green",
    near_target_met: "yellow",
    target_not_met: "red",
    debt_target_met: "grey",
    unknown: "white"
}
export const STATUS_COLORS_RGB = {
    target_not_met: "rgb(211,59,55)",
    target_met: "rgb(30,148,78)",
    near_target_met: "rgb(253,197,54)",
    debt_target_met: "rgb(150,150,150)",
    informative: "rgb(0,165,255)",
    unknown: "rgb(245,245,245)"
}
export const STATUS_NAME = {
    informative: "Informative",
    target_met: "Target met",
    near_target_met: "Near target met",
    target_not_met: "Target not met",
    debt_target_met: "Technical debt target met",
    unknown: "Unknown"
}
export const STATUS_DESCRIPTION = {
    "informative": `${STATUS_NAME.informative}: the measurement value is not evaluated against a target value.`,
    "target_met": `${STATUS_NAME.target_met}: the measurement value meets the target value.`,
    "near_target_met": `${STATUS_NAME.near_target_met}: the measurement value is close to the target value.`,
    "target_not_met": `${STATUS_NAME.target_not_met}: the measurement value does not meet the target value.`,
    "debt_target_met": <>{`${STATUS_NAME.debt_target_met}: the measurement value does not meet the\ntarget value, but this is accepted as `}<HyperLink url="https://en.wikipedia.org/wiki/Technical_debt">technical debt</HyperLink>{". The measurement\nvalue does meet the technical debt target."}</>,
    "unknown": `${STATUS_NAME.unknown}: the status could not be determined because no sources have\nbeen configured for the metric yet or the measurement data could not\nbe collected.`
}

export function getMetricDirection(metric, dataModel) {
    // Old versions of the datamodel may contain the unicode version of the direction, be prepared:
    return { "≦": "<", "≧": ">", "<": "<", ">": ">" }[metric.direction || dataModel.metrics[metric.type].direction];
}

export function formatMetricDirection(metric, dataModel) {
    return { "<": "≦", ">": "≧" }[getMetricDirection(metric, dataModel)];
}

export function get_metric_name(metric, datamodel) {
    return metric.name || datamodel.metrics[metric.type].name;
}

export function get_source_name(source, datamodel) {
    return source.name || datamodel.sources[source.type].name;
}

export function get_subject_name(subject, datamodel) {
    return subject.name || datamodel.subjects[subject.type].name;
}

export function get_metric_target(metric) {
    return metric.target || "0";
}

export function getMetricUnit(metric, dataModel) {
    return metric.unit || dataModel.metrics[metric.type].unit || "";
}

export function getMetricResponseDeadline(metric, report) {
    let deadline = null;
    const status = metric.status || "unknown"
    if (status === "debt_target_met") {
        if (metric.debt_end_date) {
            deadline = new Date(metric.debt_end_date)
        }
    } else if (status in defaultDesiredResponseTimes && metric.status_start) {
        deadline = new Date(metric.status_start)
        deadline.setDate(deadline.getDate() + getMetricDesiredResponseTime(report, status))
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
    let previousStatus;
    const consolidatedMeasurements = [];
    const filteredMeasurements = measurements.filter((measurement) => measurement.metric_uuid === metric_uuid)
    filteredMeasurements.forEach((measurement) => {
        const status = measurement?.[scale]?.status || "unknown"
        if (status === previousStatus) {
            consolidatedMeasurements.at(-1).end = measurement.end  // Status unchanged so merge this measurement with the previous one
        } else {
            consolidatedMeasurements.push(measurement);  // Status changed or first one, so keep this measurement
        }
        previousStatus = status
    })
    return consolidatedMeasurements
}

export function getMetricResponseOverrun(metric_uuid, metric, report, measurements, dataModel) {
    const consolidatedMeasurements = getMetricResponseOverruns(metric_uuid, metric, measurements, dataModel)
    const scale = getMetricScale(metric, dataModel)
    let totalOverrun = 0;  // Amount of time the desired response time was not achieved for this metric
    const overruns = []
    consolidatedMeasurements.forEach((measurement) => {
        const status = measurement?.[scale]?.status || "unknown"
        if (status in defaultDesiredResponseTimes) {
            const desiredResponseTime = getMetricDesiredResponseTime(report, status) * MILLISECONDS_PER_DAY;
            const actualResponseTime = (new Date(measurement.end)).getTime() - (new Date(measurement.start)).getTime()
            const overrun = Math.max(0, actualResponseTime - desiredResponseTime)
            if (overrun > 0) {
                overruns.push(
                    {
                        status: status,
                        start: measurement.start,
                        end: measurement.end,
                        desired_response_time: days(desiredResponseTime),
                        actual_response_time: days(actualResponseTime),
                        overrun: days(overrun)
                    }
                )
                totalOverrun += overrun
            }
        }
    })
    return { totalOverrun: days(totalOverrun), overruns: overruns }
}

function getMetricDesiredResponseTime(report, status) {
    // Precondition: status is a key of defaultDesiredResponseTimes
    return report?.desired_response_times?.[status] ?? defaultDesiredResponseTimes[status]
}

export function getMetricValue(metric, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    return metric?.latest_measurement?.[scale]?.value ?? '';
}

export function get_metric_comment(metric) {
    return metric.comment ?? '';
}

export function getMetricScale(metric, dataModel) {
    return metric.scale || dataModel.metrics[metric.type].default_scale || "count"
}

export function get_metric_status(metric) {
    return metric.status ?? '';
}

export function getStatusName(status) {
    return {
        target_met: 'Target met', near_target_met: 'Near target met', debt_target_met: 'Debt target met',
        target_not_met: 'Target not met', informative: 'Informative', unknown: 'Unknown'
    }[status || "unknown"];
}
getStatusName.propTypes = {
    status: string,
}

export function getMetricTags(metric) {
    const tags = metric.tags ?? [];
    sortWithLocaleCompare(tags)
    return tags
}
getMetricTags.propTypes = {
    metric: metricPropType
}

export function sortWithLocaleCompare(strings) {
    strings.sort((string1, string2) => string1.localeCompare(string2))
}
sortWithLocaleCompare.propTypes = {
    strings: stringsPropType
}

export function visibleMetrics(metrics, metricsToHide, hiddenTags) {
    if (metricsToHide === "all") {return {}}
    const visible = {}
    Object.entries(metrics).forEach(([metric_uuid, metric]) => {
        if ((metricsToHide === "no_action_needed") && (["target_met", "debt_target_met", "informative"].includes(metric.status))) { return }
        if (hiddenTags?.length > 0 && hiddenTags?.filter(hiddenTag => metric.tags?.includes(hiddenTag)).length >= metric.tags?.length) { return }
        visible[metric_uuid] = metric
    })
    return visible
}

export function getReportTags(report, hiddenTags) {
    const tags = new Set();
    Object.values(report.subjects).forEach((subject) => {
        Object.values(subject.metrics).forEach((metric) => {
            getMetricTags(metric).forEach((tag) => {
                if (!(hiddenTags ?? []).includes(tag)) {
                    tags.add(tag)
                }
            })
        })
    })
    const sortedTags = Array.from(tags);
    sortWithLocaleCompare(sortedTags)
    return sortedTags
}

export function getReportsTags(reports) {
    const tags = new Set();
    reports.forEach((report) => {
        getReportTags(report).forEach((tag) => tags.add(tag))
    });
    const sortedTags = Array.from(tags);
    sortWithLocaleCompare(sortedTags)
    return sortedTags
}

export function nrMetricsInReport(report) {
    let nrMetrics = 0;
    Object.values(report.subjects).forEach((subject) => {
        nrMetrics += Object.keys(subject.metrics).length;
    });
    return nrMetrics
}
nrMetricsInReport.propTypes = {
    report: reportPropType
}

export function nrMetricsInReports(reports) {
    let nrMetrics = 0;
    reports.forEach((report) => {
        nrMetrics += nrMetricsInReport(report)
    })
    return nrMetrics
}
nrMetricsInReport.propTypes = {
    reports: reportsPropType
}

export function getMetricIssueIds(metric) {
    let issueIds = metric.issue_ids ?? [];
    sortWithLocaleCompare(issueIds);
    return issueIds
}
getMetricIssueIds.propTypes = {
    metric: metricPropType
}

export function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

export function pluralize(word, count) {
    // Pluralize (naively; it doesn't work for words like sheep) the word if count > 1
    return word + (count === 1 ? "" : "s");
}

export function nice_number(number) {
    let rounded_numbers = [10, 12, 15, 20, 30, 50, 75];
    do {
        for (let rounded_number of rounded_numbers) {
            if (number <= ((9 * rounded_number) / 10)) {
                return rounded_number
            }
        }
        rounded_numbers = rounded_numbers.map((value) => { return value * 10 });
    }
    while (true);  // eslint-disable-line no-constant-condition
}

export function scaled_number(number) {
    const scale = ['', 'k', 'm'];
    const exponent = Math.floor(Math.log(number) / Math.log(1000));
    return (number / Math.pow(1000, exponent)).toFixed(0) + scale[exponent];
}

export function formatMetricScale(metric, dataModel) {
    const scale = getMetricScale(metric, dataModel)
    return scale === "percentage" ? "%" : "";
}

export function formatMetricScaleAndUnit(metric, dataModel) {
    const scale = formatMetricScale(metric, dataModel);
    const unit = getMetricUnit(metric, dataModel);
    const sep = unit ? " " : "";
    return `${scale}${sep}${unit}`;
}

export function days(timeInMs) {
    return Math.round(timeInMs / MILLISECONDS_PER_DAY)
}

export function isValidDate_YYYYMMDD(string) {
    if (/^\d{4}-\d{2}-\d{2}$/.test(string)) {
        const milliseconds_since_epoch = Date.parse(string);
        return !isNaN(milliseconds_since_epoch)
    }
    return false
}

export function toISODateStringInCurrentTZ(date) {
    // Return an ISO date string without changing the timezone to UTC as Date.toISOString does
    return `${String(date.getFullYear())}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`
}

export function getUserPermissions(username, email, report_date, permissions) {
    if (username === null || report_date !== null) { return [] }
    return PERMISSIONS.filter((permission) => {
        const permittedUsers = permissions?.[permission] ?? [];
        return permittedUsers.length === 0 ? true : permittedUsers.includes(username) || permittedUsers.includes(email)
    });
}

export function userPrefersDarkMode(uiMode) {
    return uiMode === "dark" || (uiMode === "follow_os" && window.matchMedia?.('(prefers-color-scheme: dark)').matches)
}

export function dropdownOptions(options) {
    return options.map(option => ({ key: option, text: option, value: option }))
}

export function slugify(name) {
    return `#${name?.toLowerCase().replaceAll(" ", "-").replaceAll("(", "").replaceAll(")", "")}`
}

export function sum(object) {
    const list = typeof object == Array ? object : Object.values(object)
    return list.reduce((a, b) => a + b, 0)
}
sum.propTypes = {
    object: oneOf([arrayOf(number), objectOf(number)]),
}
