import { Box, Stack } from "@mui/material"
import { bool, oneOf, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { StatusIcon } from "../measurement/StatusIcon"
import { childrenPropType, metricPropType, scalePropType } from "../sharedPropTypes"
import {
    capitalize,
    formatMetricDirection,
    formatMetricScaleAndUnit,
    formatMetricValue,
    getMetricScale,
} from "../utils"
import { STATUS_SHORT_NAME, statusPropType } from "./status"

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
    return (
        active &&
        (direction === "≦"
            ? smallerThan(metric.target, metric.debt_target)
            : smallerThan(metric.debt_target, metric.target))
    )
}

function ColoredSegment({ children, color, show, status }) {
    if (show === false) {
        return null
    }
    return (
        <Box sx={{ padding: "10px", border: "12px solid", borderColor: `${status}.main`, width: "100%" }}>
            <Stack alignItems="center" direction="row" justifyContent="space-around" spacing={2}>
                {STATUS_SHORT_NAME[status]}
                <StatusIcon status={status} />
                {capitalize(color)}
                <b>{children}</b>
            </Stack>
        </Box>
    )
}
ColoredSegment.propTypes = {
    children: childrenPropType,
    color: string,
    show: bool,
    status: statusPropType,
}

function BlueSegment({ unit }) {
    return <ColoredSegment color="blue" status="informative">{`${unit} are not evaluated`}</ColoredSegment>
}
BlueSegment.propTypes = {
    unit: string,
}

function GreenSegment({ direction, scale, target, show, unit }) {
    return (
        <ColoredSegment
            color="green"
            show={show}
            status="target_met"
        >{`${direction} ${formatMetricValue(scale, target)}${unit}`}</ColoredSegment>
    )
}
GreenSegment.propTypes = {
    direction: oneOf(["≦", "≧"]),
    scale: scalePropType,
    target: string,
    show: bool,
    unit: string,
}

function RedSegment({ direction, scale, target, show, unit }) {
    if (direction === "<" && target === "0") {
        return null
    }
    return (
        <ColoredSegment
            color="red"
            show={show}
            status="target_not_met"
        >{`${direction} ${formatMetricValue(scale, target)}${unit}`}</ColoredSegment>
    )
}
RedSegment.propTypes = {
    direction: oneOf(["<", ">"]),
    scale: scalePropType,
    target: string,
    show: bool,
    unit: string,
}

function GreySegment({ lowTarget, highTarget, scale, show, unit }) {
    return (
        <ColoredSegment
            color="grey"
            show={show}
            status="debt_target_met"
        >{`${formatMetricValue(scale, lowTarget)} - ${formatMetricValue(scale, highTarget)}${unit}`}</ColoredSegment>
    )
}
GreySegment.propTypes = {
    lowTarget: string,
    highTarget: string,
    scale: scalePropType,
    show: bool,
    unit: string,
}

function YellowSegment({ lowTarget, highTarget, scale, show, unit }) {
    if (!smallerThan(lowTarget, highTarget)) {
        return null
    }
    return (
        <ColoredSegment
            color="yellow"
            show={show}
            status="near_target_met"
        >{`${formatMetricValue(scale, lowTarget)} - ${formatMetricValue(scale, highTarget)}${unit}`}</ColoredSegment>
    )
}
YellowSegment.propTypes = {
    lowTarget: string,
    highTarget: string,
    scale: scalePropType,
    show: bool,
    unit: string,
}

function ColoredSegments({ children }) {
    return <Stack direction="row">{children}</Stack>
}
ColoredSegments.propTypes = {
    children: childrenPropType,
}

export function TargetVisualiser({ metric }) {
    const dataModel = useContext(DataModel)
    const unit = formatMetricScaleAndUnit(metric, dataModel)
    if (metric.evaluate_targets === false) {
        return (
            <ColoredSegments>
                <BlueSegment unit={unit} />
            </ColoredSegments>
        )
    }
    const direction = formatMetricDirection(metric, dataModel)
    const scale = getMetricScale(metric, dataModel)
    const oppositeDirection = { "≦": ">", "≧": "<" }[direction]
    const target = metric.target
    const nearTarget = metric.near_target
    const debtTarget = metric.debt_target
    const debtTargetApplies = debtTargetActive(metric, direction)
    if (direction === "≦") {
        return (
            <ColoredSegments>
                <GreenSegment direction={direction} scale={scale} target={target} unit={unit} />
                <GreySegment
                    lowTarget={target}
                    highTarget={debtTarget}
                    scale={scale}
                    unit={unit}
                    show={debtTargetApplies}
                />
                <YellowSegment
                    lowTarget={debtTargetApplies ? maxTarget(debtTarget, target) : target}
                    highTarget={nearTarget}
                    scale={scale}
                    unit={unit}
                />
                <RedSegment
                    direction={oppositeDirection}
                    target={debtTargetApplies ? maxTarget(nearTarget, debtTarget) : maxTarget(nearTarget, target)}
                    scale={scale}
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
                    scale={scale}
                    unit={unit}
                />
                <YellowSegment
                    lowTarget={nearTarget}
                    highTarget={debtTargetApplies ? debtTarget : target}
                    scale={scale}
                    unit={unit}
                />
                <GreySegment
                    lowTarget={debtTarget}
                    highTarget={target}
                    scale={scale}
                    unit={unit}
                    show={debtTargetApplies}
                />
                <GreenSegment direction={direction} scale={scale} target={target} unit={unit} />
            </ColoredSegments>
        )
    }
}
TargetVisualiser.propTypes = {
    metric: metricPropType,
}
