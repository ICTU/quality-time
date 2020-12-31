import { parse, stringify } from 'query-string';
import React, { useEffect, useState } from 'react';
import { toast } from 'react-semantic-toasts';

export function get_metric_direction(metric, data_model) {
    return format_metric_direction(metric.direction || data_model.metrics[metric.type].direction);
}

export function format_metric_direction(direction) {
    return { "<": "≦", ">": "≧" }[direction];
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

export function show_message(type, title, description, icon) {
    toast({
        title: title,
        type: type,
        icon: icon,
        size: "large",
        description: <p>{description}</p>,
        time: 30000
    }, () => { }, () => { }, () => { });  // Event handlers are mandatory
}

export function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
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

export function format_minutes(number) {
    const hours = Math.floor(number / 60);
    const minutes = number - hours * 60;
    const leading_zero = minutes < 10 ? "0" : "";
    return `${hours}:${leading_zero}${minutes}`
}

export function formatMetricUnit(metricType, metric, withMultiple = true) {
    let metric_type_unit = metricType.unit;
    if (withMultiple) {
        metric_type_unit = metricType.unit === 'minutes' && metric.scale !== 'percentage' ? 'hours' : metricType.unit;
    }
    return `${metric.unit || metric_type_unit}`;
}

export function formatMetricScale(metric) {
    return metric.scale === "percentage" ? "% " : " ";
}

export function formatMetricScaleAndUnit(metricType, metric, withMultiple = true) {
    return `${formatMetricScale(metric)}${formatMetricUnit(metricType, metric, withMultiple)}`;
}

export function useURLSearchQuery(history, key, state_type, default_value) {
    // state_type can either be "boolean", "integer", or "array"
    const [state, setState] = useState(getState());

    function getState() {
        const parsed_state = parseURLSearchQuery()[key];
        if (state_type === "boolean") {
            return parsed_state === "true"
        } else if (state_type === "integer") {
            return typeof parsed_state === "string" ? parseInt(parsed_state, 10) : default_value;
        }
        // else state_type is "array"
        return typeof parsed_state === "string" && parsed_state !== "" ? [parsed_state] : parsed_state || []
    }

    function parseURLSearchQuery() {
        return parse(history.location.search, { arrayFormat: 'comma' });
    }

    function setURLSearchQuery(new_state) {
        let parsed = parseURLSearchQuery();
        parsed[key] = new_state || "";
        const search = stringify(parsed, { skipEmptyString: true, arrayFormat: 'comma' });
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

export function useDelayedRender() {
    const [visible, setVisible] = useState(false);
    useEffect(() => { setTimeout(setVisible, 50, true) }, []);
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