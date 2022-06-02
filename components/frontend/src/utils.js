import { useEffect, useState } from 'react';
import { PERMISSIONS } from './context/Permissions';

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
    return (metric.accept_debt ? metric.debt_target : metric.target) || "0";
}

export function getMetricUnit(metric, dataModel) {
    const metricType = dataModel.metrics[metric.type];
    return formatMetricUnit(metricType, metric)
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

export function decapitalize(string) {
    if (string.match(/^[A-Z][A-Z]/)) {
        return string // Don't decapitalize strings that start with an abbrevation
    }
    return string.charAt(0).toLowerCase() + string.slice(1);
}

export function pluralize(word, count) {
    // Pluralize (naively; it doesn't work for words like sheep) the word if count > 1
    return word + (count === 1 ? "" : "s");
}

export function nice_number(number) {
    let rounded_numbers = [20, 50, 100];
    do {
        for (var rounded_number of rounded_numbers) {
            if (number <= ((4 * rounded_number) / 5)) {
                return rounded_number
            }
        }
        rounded_numbers = rounded_numbers.map((value) => { return value * 10 });
    }
    while (true);
}

export function scaled_number(number) {
    var scale = ['', 'k', 'm'];
    var exponent = Math.floor(Math.log(number) / Math.log(1000));
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

const registeredURLSearchQueryKeys = new Set(["report_date", "report_url"]);

export function useURLSearchQuery(history, key, state_type, default_value) {
    // state_type can either be "boolean", "integer", "string", or "array"
    const [state, setState] = useState(getState());
    registeredURLSearchQueryKeys.add(key);

    function getState() {
        const parsed_state = parseURLSearchQuery().get(key);
        if (state_type === "boolean") {
            return parsed_state === "true"
        } else if (state_type === "integer") {
            return typeof parsed_state === "string" ? parseInt(parsed_state, 10) : default_value;
        } else if (state_type === "string") {
            return parsed_state ?? default_value
        }
        // else state_type is "array"
        return parsed_state?.split(",") ?? []
    }

    function parseURLSearchQuery() {
        return new URLSearchParams(history.location.search)
    }

    function setURLSearchQuery(new_state) {
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

    function clearURLSearchQuery() {
        setURLSearchQuery([]);
    }

    return state_type === "array" ? [state, toggleURLSearchQuery, clearURLSearchQuery] : [state, setURLSearchQuery]
}

export function registeredURLSearchParams(history) {
    // Return registered URL search parameters only; to prevent CodeQL js/client-side-unvalidated-url-redirection
    let parsed = new URLSearchParams(history.location.search)
    for (var key of parsed.keys()) {
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

export function isValidDate_DDMMYYYY(string) {
    if (/^\d{1,2}-\d{1,2}-\d{4}$/.test(string)) {
        return isValidDate_YYYYMMDD(string.split("-").reverse().join("-"))
    }
    return false
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
