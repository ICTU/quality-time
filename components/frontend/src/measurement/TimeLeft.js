import React from 'react';
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { days, getMetricResponseDeadline, getMetricResponseTimeLeft, pluralize } from '../utils';

function noActionRequired(metric) {
    return (["target_met", "informative"].indexOf(metric.status) >= 0)
}

function acceptedDebtWithoutEndDate(metric) {
    return (metric.status === "debt_target_met" && !metric.debt_end_date)
}

export function TimeLeft({ metric, report }) {
    if (noActionRequired(metric) || acceptedDebtWithoutEndDate(metric) || !metric.status_start) {
        return null
    }
    const deadline = getMetricResponseDeadline(metric, report)
    const timeLeft = getMetricResponseTimeLeft(metric, report)
    const daysLeft = days(Math.max(0, timeLeft))
    const triggerText = `${daysLeft} ${pluralize("day", daysLeft)}`
    let deadlineLabel = "Deadline to address this metric was"
    let trigger = <Label color="red">{triggerText}</Label>
    if (timeLeft >= 0) {
        deadlineLabel = "Time left to address this metric is"
        trigger = <span>{triggerText}</span>
    }
    return (
        <Popup flowing hoverable trigger={trigger}>
            <TimeAgoWithDate date={deadline}>{deadlineLabel}</TimeAgoWithDate>.
        </Popup>
    )
}
