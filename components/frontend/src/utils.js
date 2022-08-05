import { useEffect, useState } from 'react';
import { get_settings } from './api/settings';
import { PERMISSIONS } from './context/Permissions';
import { metricReactionDeadline } from './defaults';

export const MILLISECONDS_PER_HOUR = 60 * 60 * 1000;
const MILLISECONDS_PER_DAY = 24 * MILLISECONDS_PER_HOUR;


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
    const metricType = dataModel.metrics[metric.type];
    return formatMetricUnit(metricType, metric)
}

export function getMetricResponseDeadline(metric, report) {
    let deadline = null;
    if (metric.status === "debt_target_met" && metric.debt_end_date) {
        deadline = new Date(metric.debt_end_date)
    } else if ((metric.status || "unknown") in metricReactionDeadline && metric.status_start) {
        deadline = new Date(metric.status_start)
        deadline.setDate(deadline.getDate() + getMetricDesiredResponseTime(report, metric.status))
    }
    return deadline
}

export function getMetricResponseTimeLeft(metric, report) {
    const deadline = getMetricResponseDeadline(metric, report)
    const now = new Date()
    return deadline === null ? null : deadline.getTime() - now.getTime()
}

function getMetricResponseOverruns(metric_uuid, metric, measurements) {
    const scale = metric?.scale ?? "count"
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

export function getMetricResponseOverrun(metric_uuid, metric, report, measurements) {
    const consolidatedMeasurements = getMetricResponseOverruns(metric_uuid, metric, measurements)
    const scale = metric?.scale ?? "count"
    let totalOverrun = 0;  // Amount of time the desired response time was not achieved for this metric
    const overruns = []
    consolidatedMeasurements.forEach((measurement) => {
        const status = measurement?.[scale]?.status || "unknown"
        if (status in metricReactionDeadline) {
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
    return report?.desired_response_times?.[status] ?? (metricReactionDeadline[status] ?? metricReactionDeadline["unknown"])
}

export function get_metric_value(metric) {
    return metric?.latest_measurement?.[metric.scale]?.value ?? '';
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

export function get_metric_tags(metric) {
    let tags = metric.tags ?? [];
    tags.sort();
    return tags
}

export function get_metric_issue_ids(metric) {
    let issue_ids = metric.issue_ids ?? [];
    issue_ids.sort();
    return issue_ids
}

export function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

export function pluralize(word, count) {
    // Pluralize (naively; it doesn't work for words like sheep) the word if count > 1
    return word + (count === 1 ? "" : "s");
}

export function nice_number(number) {
    let rounded_numbers = [20, 50, 100];
    do {
        for (let rounded_number of rounded_numbers) {
            if (number <= ((4 * rounded_number) / 5)) {
                return rounded_number
            }
        }
        rounded_numbers = rounded_numbers.map((value) => { return value * 10 });
    }
    while (true);
}

export function scaled_number(number) {
    const scale = ['', 'k', 'm'];
    const exponent = Math.floor(Math.log(number) / Math.log(1000));
    return (number / Math.pow(1000, exponent)).toFixed(0) + scale[exponent];
}

function formatMetricUnit(metricType, metric) {
    return `${metric.unit || metricType.unit}`;
}

export function formatMetricScale(metric) {
    return metric.scale === "percentage" ? "%" : "";
}

export function formatMetricScaleAndUnit(metricType, metric) {
    const scale = formatMetricScale(metric);
    const unit = formatMetricUnit(metricType, metric);
    const sep = unit ? " " : "";
    return `${scale}${sep}${unit}`;
}

export function days(timeInMs) {
    return Math.round(timeInMs / MILLISECONDS_PER_DAY)
}

const registeredURLSearchQueryKeys = new Set(["report_date", "report_url"]);

export function useURLSearchQuery(history, key, state_type, default_value) {
    // state_type can either be "boolean", "integer", "string", or "array"
    if (state_type === "array" && !default_value) {
        default_value = []
    }

    const [state, setState] = useState(getState());
    registeredURLSearchQueryKeys.add(key);

    function getState() {
        const parsed_state = parseURLSearchQuery().get(key);
        if (state_type === "boolean") {
            return parsed_state ? parsed_state === "true" : default_value
        } else if (state_type === "integer") {
            return typeof parsed_state === "string" ? parseInt(parsed_state, 10) : default_value;
        } else if (state_type === "string") {
            return parsed_state ?? default_value
        }
        return parsed_state?.split(",") ?? default_value
    }

    function parseURLSearchQuery() {
        return new URLSearchParams(history.location.search)
    }

    function setURLSearchQuery(new_state) {
        if (state_type === "array" && !new_state) {
            new_state = default_value
        }
        let parsed = parseURLSearchQuery();
        if ((state_type === "array" && new_state.length === 0) || (new_state === default_value)) {
            parsed.delete(key)
        } else {
            parsed.set(key, new_state)
        }
        const search = parsed.toString().replace(/%2C/g, ",")  // No need to encode commas
        history.replace({ search: search.length > 0 ? "?" + search : "" });
        setState(new_state);
    }

    function toggleURLSearchQuery(...items) {
        const new_state = [];
        state.forEach((item) => { if (!items.includes(item)) { new_state.push(item) } })
        items.forEach((item) => { if (!state.includes(item)) { new_state.push(item) } })
        setURLSearchQuery(new_state);
    }

    function setDefaultValue(newDefault) {
        default_value = newDefault
    }

    return state_type === "array" ? [state, toggleURLSearchQuery, setURLSearchQuery, setDefaultValue] : [state, setURLSearchQuery, setDefaultValue]
}

export function registeredURLSearchParams(history) {
    // Return registered URL search parameters only; to prevent CodeQL js/client-side-unvalidated-url-redirection
    let parsed = new URLSearchParams(history.location.search)
    for (let key of parsed.keys()) {
        if (!registeredURLSearchQueryKeys.has(key)) { parsed.delete(key) }
    }
    return parsed
}

export function useDelayedRender() {
    const [visible, setVisible] = useState(false);
    useEffect(() => {
        const timeout = setTimeout(setVisible, 50, true);
        return () => clearTimeout(timeout)
    }, []);
    return visible;
}

export function isValidDate_YYYYMMDD(string) {
    if (/^\d{4}-\d{2}-\d{2}$/.test(string)) {
        const milliseconds_since_epoch = Date.parse(string);
        return !isNaN(milliseconds_since_epoch)
    }
    return false
}

export function getUserPermissions(username, email, current_report_is_tag_report, report_date, permissions) {
    if (username === null || report_date !== null || current_report_is_tag_report) { return [] }
    return PERMISSIONS.filter((permission) => {
        const permittedUsers = permissions?.[permission] ?? [];
        return permittedUsers.length === 0 ? true : permittedUsers.includes(username) || permittedUsers.includes(email)
    });
}

export function userPrefersDarkMode(uiMode) {
    return uiMode === "dark" || (uiMode === null && window.matchMedia?.('(prefers-color-scheme: dark)').matches)
}

export function dropdownOptions(options) {
    return options.map(option => ({ key: option, text: option, value: option }))
}

export function slugify(name) {
    return `#${name?.toLowerCase().replaceAll(" ", "-").replaceAll("(", "").replaceAll(")", "")}`
}

export const DEFAULT_SETTINGS = {
    date_interval: 7,
    date_order: "descending",
    hidden_columns: [],
    hide_metrics_not_requiring_action: false,
    nr_dates: 1,
    sort_column: null,
    sort_direction: "ascending",
    tabs: [],
    show_issue_summary: false,
    show_issue_creation_date: false,
    show_issue_update_date: false,
    show_issue_due_date: false,
    show_issue_release: false,
    show_issue_sprint: false,
    ui_mode: null
}

export async function getDefaultSettings() {
    const settingsResponse = await get_settings()
    return {...DEFAULT_SETTINGS, ...settingsResponse.settings}
}
