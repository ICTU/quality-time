import React, { useContext } from 'react';
import { Segment } from 'semantic-ui-react';
import { Icon, Popup } from '../semantic_ui_react_wrappers';
import { IntegerInput } from '../fields/IntegerInput';
import { StringInput } from '../fields/StringInput';
import { set_metric_attribute } from '../api/metric';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { formatMetricDirection, formatMetricScaleAndUnit, getMetricDirection } from '../utils';

function TargetVisualiser({metric}) {
    const dataModel = useContext(DataModel);
    if (!metric.evaluate_targets) {
        return (
            <Segment.Group horizontal>
                <Segment inverted color="blue"><b>All values are blue (informative)</b></Segment>
            </Segment.Group>
        )
    }
    const direction = formatMetricDirection(metric, dataModel);
    const oppositeDirection = { "≦": "≧", "≧": "≦" }[direction]
    const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric)
    const target = `${metric.target}${unit}`
    const minTarget = `${Math.min(metric.target, metric.near_target)}${unit}`
    const maxTarget = `${Math.max(metric.target, metric.near_target)}${unit}`
    if (getMetricDirection(metric, dataModel) === "<") {
        return (
            <Segment.Group horizontal>
                <Segment inverted color="green"><b>{`${direction} ${target} is green (target met)`}</b></Segment>
                {metric.near_target.localeCompare(metric.target, undefined, {numeric: true}) <= 0 ?
                    <Segment inverted><b>{`no yellow (near target) because near target ${direction} target`}</b></Segment>
                :
                    <Segment inverted color="yellow"><b>{`${minTarget} - ${maxTarget} is yellow (near target)`}</b></Segment>
                }
                <Segment inverted color="red"><b>{`${oppositeDirection} ${maxTarget} is red (target not met)`}</b></Segment>
            </Segment.Group>
        )
    } else {
        return (
            <Segment.Group horizontal>
                <Segment inverted color="red"><b>{`${oppositeDirection} ${minTarget} is red (target not met)`}</b></Segment>
                {metric.near_target.localeCompare(metric.target, undefined, {numeric: true}) >= 0 ?
                    <Segment inverted><b>{`no yellow (near target) because near target ${direction} target`}</b></Segment>
                :
                    <Segment inverted color="yellow"><b>{`${minTarget} - ${maxTarget} is yellow (near target)`}</b></Segment>
                }
                <Segment inverted color="green"><b>{`${direction} ${target} is green (target met)`}</b></Segment>
            </Segment.Group>
        )
    }
}

export function TargetLabel({label, metric, position, targetType}) {
    const dataModel = useContext(DataModel);
    const metricType = dataModel.metrics[metric.type];
    const defaultTarget = metricType[targetType];
    const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric);
    const defaultTargetLabel = defaultTarget === metric[targetType] || defaultTarget === undefined ? '' : ` (default: ${defaultTarget} ${unit})`;
    return (
        <label>{label + defaultTargetLabel} <Popup
            content={<TargetVisualiser metric={metric}/>}
            flowing
            header="How measurement values are evaluated"
            on={['hover', 'focus']}
            position={position}
            trigger={<Icon tabIndex="0" name="help circle" />} />
        </label>
    )
}

export function Target({ metric, metric_uuid, target_type, label, reload }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metric_scale = metric.scale || metricType.default_scale || "count";
    // Old versions of the datamodel may contain the unicode version of the direction, be prepared:
    const metric_direction = { "≦": "<", "≧": ">", "<": "<", ">": ">" }[metric.direction || metricType.direction];
    const metric_direction_prefix = { "<": "≦", ">": "≧" }[metric_direction];
    const targetValue = metric[target_type];
    const metric_unit_without_percentage = metric.unit || metricType.unit;
    const metric_unit = `${metric_scale === "percentage" ? "% " : ""}${metric_unit_without_percentage}`;
    if (metric_scale === "version_number") {
        return (
            <StringInput
                label={label}
                prefix={metric_direction_prefix}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                set_value={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                value={targetValue}
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
                set_value={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                unit={metric_unit}
                value={targetValue}
            />
        );
    }

}
