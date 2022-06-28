import React, { useContext } from 'react';
import { Segment } from 'semantic-ui-react';
import { Icon, Popup } from '../semantic_ui_react_wrappers';
import { IntegerInput } from '../fields/IntegerInput';
import { StringInput } from '../fields/StringInput';
import { set_metric_attribute } from '../api/metric';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { formatMetricDirection, formatMetricScaleAndUnit, getMetricDirection, getMetricScale } from '../utils';

function TargetVisualiser({metric}) {
    const dataModel = useContext(DataModel);
    if (metric.evaluate_targets === false) {
        return (
            <Segment.Group horizontal>
                <Segment inverted color="blue"><b>All values are blue (informative)</b></Segment>
            </Segment.Group>
        )
    }
    const direction = formatMetricDirection(metric, dataModel);
    const oppositeDirection = { "≦": ">", "≧": "<" }[direction]
    const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric)
    const target = `${metric.target}${unit}`
    const minTarget = `${Math.min(metric.target, metric.near_target)}`
    const maxTarget = `${Math.max(metric.target, metric.near_target)}`
    if (getMetricDirection(metric, dataModel) === "<") {
        return (
            <Segment.Group horizontal>
                <Segment inverted color="green"><b>{`${direction} ${target} is green (target met)`}</b></Segment>
                {metric.near_target.localeCompare(metric.target, undefined, {numeric: true}) <= 0 ?
                    <Segment inverted><b>{`no yellow (near target) because near target ${direction} target`}</b></Segment>
                :
                    <Segment inverted color="yellow"><b>{`${minTarget} - ${maxTarget}${unit} is yellow (near target)`}</b></Segment>
                }
                <Segment inverted color="red"><b>{`${oppositeDirection} ${maxTarget}${unit} is red (target not met)`}</b></Segment>
            </Segment.Group>
        )
    } else {
        return (
            <Segment.Group horizontal>
                <Segment inverted color="red"><b>{`${oppositeDirection} ${minTarget}${unit} is red (target not met)`}</b></Segment>
                {metric.near_target.localeCompare(metric.target, undefined, {numeric: true}) >= 0 ?
                    <Segment inverted><b>{`no yellow (near target) because near target ${direction} target`}</b></Segment>
                :
                    <Segment inverted color="yellow"><b>{`${minTarget} - ${maxTarget}${unit} is yellow (near target)`}</b></Segment>
                }
                <Segment inverted color="green"><b>{`${direction} ${target} is green (target met)`}</b></Segment>
            </Segment.Group>
        )
    }
}

function TargetLabel({label, metric, position, targetType}) {
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

export function Target({ metric, metric_uuid, target_type, label, labelPosition, reload }) {
    const dataModel = useContext(DataModel)
    const metricScale = getMetricScale(metric, dataModel)
    const metricDirectionPrefix = formatMetricDirection(metric, dataModel)
    const targetValue = metric[target_type];
    const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric);
    const targetLabel = <TargetLabel label={label} metric={metric} position={labelPosition} targetType={target_type} />
    if (metricScale === "version_number") {
        return (
            <StringInput
                label={targetLabel}
                prefix={metricDirectionPrefix}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                set_value={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                value={targetValue}
            />
        )
    } else {
        const max = metricScale === "percentage" ? "100" : null;
        return (
            <IntegerInput
                label={targetLabel}
                max={max}
                min="0"
                prefix={metricDirectionPrefix}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                set_value={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                unit={unit}
                value={targetValue}
            />
        );
    }
}
