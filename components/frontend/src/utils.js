import React from 'react';
import { toast } from 'react-semantic-toasts';

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