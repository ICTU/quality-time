import React, { useContext } from 'react';
import { Segment } from 'semantic-ui-react';
import { Header, Icon, Popup } from '../semantic_ui_react_wrappers';
import { IntegerInput } from '../fields/IntegerInput';
import { StringInput } from '../fields/StringInput';
import { set_metric_attribute } from '../api/metric';
import { DataModel } from '../context/DataModel';
import { DarkMode } from '../context/DarkMode';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { StatusIcon } from '../measurement/StatusIcon';
import { capitalize, formatMetricDirection, formatMetricScaleAndUnit, getMetricScale, getStatusName } from '../utils';


function ColoredSegment({ children, color, show, status }) {
    const darkMode = useContext(DarkMode);
    if (show === false) {
        return null
    }
    return (
        <Segment inverted color={color}>
            <Segment inverted={darkMode}>
                <Header><span>{getStatusName(status)} <StatusIcon status={status} size="tiny" /></span><Header.Subheader>{capitalize(color)}</Header.Subheader></Header>
                <b>{children}</b>
            </Segment>
        </Segment>
    )
}

function BlueSegment({ unit }) {
    return (
        <ColoredSegment color="blue" status="informative">{`${unit} are not evaluated`}</ColoredSegment>
    )
}

function GreenSegment({ direction, target, show, unit }) {
    return (
        <ColoredSegment color="green" show={show} status="target_met">{`${direction} ${target}${unit}`}</ColoredSegment>
    )
}

function RedSegment({ direction, target, show, unit }) {
    if (direction === "<" && target === "0") {
        return null
    }
    return (
        <ColoredSegment color="red" show={show} status="target_not_met">{`${direction} ${target}${unit}`}</ColoredSegment>
    )
}

function GreySegment({ lowTarget, highTarget, show, unit }) {
    return (
        <ColoredSegment color="grey" show={show} status="debt_target_met">{`${lowTarget} - ${highTarget}${unit}`}</ColoredSegment>
    )
}

function YellowSegment({ lowTarget, highTarget, show, unit }) {
    return (
        <ColoredSegment color="yellow" show={show} status="near_target_met">{`${lowTarget} - ${highTarget}${unit}`}</ColoredSegment>
    )
}

function ColoredSegments({ children }) {
    return (
        <Segment.Group horizontal size="tiny">
            {children}
        </Segment.Group>
    )
}


function smallerThan(target1, target2) {
    const t1 = target1 ?? "0"
    const t2 = target2 ?? "0"
    return t1.localeCompare(t2, undefined, { numeric: true }) < 0
}

function maxTarget(...targets) {
    targets.sort((target1, target2) => target1.localeCompare(target2, undefined, { numeric: true }))
    return targets.at(-1)
}

function minTarget(...targets) {
    targets.sort((target1, target2) => target1.localeCompare(target2, undefined, { numeric: true }))
    return targets.at(0)
}

function TargetVisualiser({ metric }) {
    const dataModel = useContext(DataModel);
    const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric)
    if (metric.evaluate_targets === false) {
        return (
            <ColoredSegments>
                <BlueSegment unit={unit} />
            </ColoredSegments>
        )
    }
    const direction = formatMetricDirection(metric, dataModel);
    const oppositeDirection = { "≦": ">", "≧": "<" }[direction]
    const target = metric.target
    const nearTarget = metric.near_target
    const debtTarget = metric.debt_target
    const debtTargetSmallerThanNearTarget = smallerThan(debtTarget, nearTarget)
    const debtTargetSmallerThanTarget = smallerThan(debtTarget, target)
    const targetSmallerThanDebtTarget = smallerThan(target, debtTarget)
    const targetSmallerThanNearTarget = smallerThan(target, nearTarget)
    const nearTargetSmallerThanTarget = smallerThan(nearTarget, target)
    const nearTargetSmallerThanDebtTarget = smallerThan(nearTarget, debtTarget)
    const endDate = metric.debt_end_date ? new Date(metric.debt_end_date) : null
    let debtTargetApplies = !!metric.accept_debt && ((endDate && endDate >= new Date()) || !endDate)
    if (direction === "≦") {
        debtTargetApplies = debtTargetApplies && targetSmallerThanDebtTarget;
        return (
            <ColoredSegments>
                <GreenSegment direction={direction} target={target} unit={unit} />
                <GreySegment lowTarget={target} highTarget={debtTarget} unit={unit} show={debtTargetApplies} />
                <YellowSegment
                    lowTarget={debtTargetApplies ? maxTarget(debtTarget, target) : target}
                    highTarget={nearTarget}
                    unit={unit}
                    show={targetSmallerThanNearTarget && (debtTargetApplies ? debtTargetSmallerThanNearTarget : true)}
                />
                <RedSegment
                    direction={oppositeDirection}
                    target={debtTargetApplies ? maxTarget(nearTarget, debtTarget) : maxTarget(nearTarget, target)}
                    unit={unit}
                />
            </ColoredSegments>
        )
    } else {
        debtTargetApplies = debtTargetApplies && debtTargetSmallerThanTarget;
        return (
            <ColoredSegments>
                <RedSegment
                    direction={oppositeDirection}
                    target={debtTargetApplies ? minTarget(debtTarget, nearTarget) : minTarget(nearTarget, target)}
                    unit={unit}
                />
                <YellowSegment
                    lowTarget={nearTarget}
                    highTarget={debtTargetApplies ? debtTarget : target}
                    unit={unit}
                    show={nearTargetSmallerThanTarget && (debtTargetApplies ? nearTargetSmallerThanDebtTarget : true)}
                />
                <GreySegment lowTarget={debtTarget} highTarget={target} unit={unit} show={debtTargetApplies} />
                <GreenSegment direction={direction} target={target} unit={unit} />
            </ColoredSegments>
        )
    }
}

function TargetLabel({ label, metric, position, targetType }) {
    const dataModel = useContext(DataModel);
    const metricType = dataModel.metrics[metric.type];
    const defaultTarget = metricType[targetType];
    const unit = formatMetricScaleAndUnit(dataModel.metrics[metric.type], metric);
    const defaultTargetLabel = defaultTarget === metric[targetType] || defaultTarget === undefined ? '' : ` (default: ${defaultTarget} ${unit})`;
    return (
        <label>{label + defaultTargetLabel} <Popup
            content={<TargetVisualiser metric={metric} />}
            flowing
            header="How measurement values are evaluated"
            on={['hover', 'focus']}
            position={position}
            trigger={<Icon role="tooltip" tabIndex="0" name="help circle" />} />
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
