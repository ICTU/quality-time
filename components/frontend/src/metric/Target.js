import React, { useContext } from 'react';
import { IntegerInput } from '../fields/IntegerInput';
import { StringInput } from '../fields/StringInput';
import { set_metric_attribute } from '../api/metric';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { DataModel } from '../context/Contexts';

export function Target({ metric, metric_uuid, target_type, label, reload }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metric_scale = metric.scale || metricType.default_scale || "count";
    // Old versions of the datamodel may contain the unicode version of the direction, be prepared:
    const metric_direction = { "≦": "<", "≧": ">", "<": "<", ">": ">" }[metric.direction || metricType.direction];
    const metric_direction_prefix = { "<": "≦", ">": "≧" }[metric_direction];
    const default_target = metricType[target_type];
    const measurement_value = metric[target_type];
    const metric_unit_without_percentage = metric.unit || metricType.unit;
    const metric_unit = `${metric_scale === "percentage" ? "% " : ""}${metric_unit_without_percentage}`;
    const inputLabel = label + (metricType[target_type] === metric[target_type] || default_target === undefined ? '' : ` (default: ${default_target} ${metric_unit})`);
    if (metric_scale === "version_number") {
        return (
            <StringInput
                label={inputLabel}
                prefix={metric_direction_prefix}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                set_value={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                value={measurement_value}
            />
        )
    } else {
        const max = metric_scale === "percentage" ? "100" : null;
        return (
            <IntegerInput
                label={inputLabel}
                max={max}
                min="0"
                prefix={metric_direction_prefix}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                set_value={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                unit={metric_unit}
                value={measurement_value}
            />
        );
    }

}
