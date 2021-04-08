import React from 'react';
import { IntegerInput } from '../fields/IntegerInput';
import { StringInput } from '../fields/StringInput';
import { set_metric_attribute } from '../api/metric';

export function Target(props) {
    const metric_type = props.datamodel.metrics[props.metric.type];
    const metric_scale = props.metric.scale || metric_type.default_scale || "count";
    // Old versions of the datamodel may contain the unicode version of the direction, be prepared:
    const metric_direction = { "≦": "<", "≧": ">", "<": "<", ">": ">" }[props.metric.direction || metric_type.direction];
    const metric_direction_prefix = { "<": "≦", ">": "≧" }[metric_direction];
    const default_target = metric_type[props.target_type];
    const measurement_value = props.metric[props.target_type];
    const metric_unit_without_percentage = props.metric.unit || metric_type.unit;
    const metric_unit = `${metric_scale === "percentage" ? "% " : ""}${metric_unit_without_percentage}`;
    const label = props.label + (metric_type[props.target_type] === props.metric[props.target_type] || default_target === undefined ? '' : ` (default: ${default_target} ${metric_unit})`);
    if (metric_scale === "version_number") {
        return (
            <StringInput
                label={label}
                prefix={metric_direction_prefix}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                set_value={(value) => set_metric_attribute(props.metric_uuid, props.target_type, value, props.reload)}
                value={measurement_value}
            />
        )
    } else {
        const max = metric_scale === "percentage" ? "100" : null;
        return (
            <IntegerInput
                label={label}
                max={max}
                min="0"
                prefix={metric_direction_prefix}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                set_value={(value) => set_metric_attribute(props.metric_uuid, props.target_type, value, props.reload)}
                unit={metric_unit}
                value={measurement_value}
            />
        );
    }

}
