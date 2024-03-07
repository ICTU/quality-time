import { useContext } from 'react';
import { bool, func, oneOf, string } from 'prop-types';
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
import { childrenPropType, labelPropType, metricPropType, statusPropType } from '../sharedPropTypes';

function smallerThan(target1, target2) {
    const t1 = target1 ?? `${Number.POSITIVE_INFINITY}`
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

function debtTargetActive(metric, direction) {
    const endDate = metric.debt_end_date ? new Date(metric.debt_end_date) : null
    const active = !!metric.accept_debt && ((endDate && endDate >= new Date()) || !endDate)
    return active && (direction === "≦" ? smallerThan(metric.target, metric.debt_target) : smallerThan(metric.debt_target, metric.target))
}

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
ColoredSegment.propTypes = {
    children: childrenPropType,
    color: string,
    show: bool,
    status: statusPropType,
}

function BlueSegment({ unit }) {
    return (
        <ColoredSegment color="blue" status="informative">{`${unit} are not evaluated`}</ColoredSegment>
    )
}
BlueSegment.propTypes = {
    unit: string,
}

function GreenSegment({ direction, target, show, unit }) {
    return (
        <ColoredSegment color="green" show={show} status="target_met">{`${direction} ${target}${unit}`}</ColoredSegment>
    )
}
GreenSegment.propTypes = {
    direction: oneOf(["≦", "≧"]),
    target: string,
    show: bool,
    unit: string,
}

function RedSegment({ direction, target, show, unit }) {
    if (direction === "<" && target === "0") {
        return null
    }
    return (
        <ColoredSegment color="red" show={show} status="target_not_met">{`${direction} ${target}${unit}`}</ColoredSegment>
    )
}
RedSegment.propTypes = {
    direction: oneOf(["<", ">"]),
    target: string,
    show: bool,
    unit: string,
}

function GreySegment({ lowTarget, highTarget, show, unit }) {
    return (
        <ColoredSegment color="grey" show={show} status="debt_target_met">{`${lowTarget} - ${highTarget}${unit}`}</ColoredSegment>
    )
}
GreySegment.propTypes = {
    lowTarget: string,
    highTarget: string,
    show: bool,
    unit: string,
}

function YellowSegment({ lowTarget, highTarget, show, unit }) {
    if (!smallerThan(lowTarget, highTarget)) {
        return null
    }
    return (
        <ColoredSegment color="yellow" show={show} status="near_target_met">{`${lowTarget} - ${highTarget}${unit}`}</ColoredSegment>
    )
}
YellowSegment.propTypes = {
    lowTarget: string,
    highTarget: string,
    show: bool,
    unit: string,
}

function ColoredSegments({ children }) {
    return (
        <Segment.Group horizontal size="tiny">
            {children}
        </Segment.Group>
    )
}
ColoredSegments.propTypes = {
    children: childrenPropType,
}

function TargetVisualiser({ metric }) {
    const dataModel = useContext(DataModel);
    const unit = formatMetricScaleAndUnit(metric, dataModel)
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
    const debtTargetApplies = debtTargetActive(metric, direction)
    if (direction === "≦") {
        return (
            <ColoredSegments>
                <GreenSegment direction={direction} target={target} unit={unit} />
                <GreySegment lowTarget={target} highTarget={debtTarget} unit={unit} show={debtTargetApplies} />
                <YellowSegment
                    lowTarget={debtTargetApplies ? maxTarget(debtTarget, target) : target}
                    highTarget={nearTarget}
                    unit={unit}
                />
                <RedSegment
                    direction={oppositeDirection}
                    target={debtTargetApplies ? maxTarget(nearTarget, debtTarget) : maxTarget(nearTarget, target)}
                    unit={unit}
                />
            </ColoredSegments>
        )
    } else {
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
                />
                <GreySegment lowTarget={debtTarget} highTarget={target} unit={unit} show={debtTargetApplies} />
                <GreenSegment direction={direction} target={target} unit={unit} />
            </ColoredSegments>
        )
    }
}
TargetVisualiser.propTypes = {
    metric: metricPropType,
}

function TargetLabel({ label, metric, position, targetType }) {
    const dataModel = useContext(DataModel);
    const metricType = dataModel.metrics[metric.type];
    const defaultTarget = metricType[targetType];
    const unit = formatMetricScaleAndUnit(metric, dataModel);
    const defaultTargetLabel = defaultTarget === metric[targetType] || defaultTarget === undefined ? '' : ` (default: ${defaultTarget} ${unit})`;
    return (
        <label>{label + defaultTargetLabel} <Popup
            content={<TargetVisualiser metric={metric} />}
            flowing
            header="How measurement values are evaluated"
            hoverable
            on={['hover', 'focus']}
            position={position}
            trigger={<Icon role="tooltip" tabIndex="0" name="help circle" />} />
        </label>
    )
}
TargetLabel.propTypes = {
    label: labelPropType,
    metric: metricPropType,
    position: string,
    targetType: string,
}

export function Target({ label, labelPosition, metric, metric_uuid, reload, target_type }) {
    const dataModel = useContext(DataModel)
    const metricScale = getMetricScale(metric, dataModel)
    const metricDirectionPrefix = formatMetricDirection(metric, dataModel)
    const targetValue = metric[target_type];
    const unit = formatMetricScaleAndUnit(metric, dataModel);
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
                prefix={metricDirectionPrefix}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                set_value={(value) => set_metric_attribute(metric_uuid, target_type, value, reload)}
                unit={unit}
                value={targetValue}
            />
        );
    }
}
Target.propTypes = {
    label: labelPropType,
    labelPosition: string,
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    target_type: string,
}
