import React from 'react';
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { getMetricDeadline, getMetricTimeLeft, pluralize } from '../utils';

export function TimeLeft({ metric, report }) {
    if (["target_met", "debt_target_met", "informative"].indexOf(metric.status) >= 0 || !metric.status_start) {
        return null
    }
    const deadline = getMetricDeadline(metric, report)
    const timeLeft = getMetricTimeLeft(metric, report)
    const daysLeft = Math.max(0, Math.round(timeLeft / (24 * 60 * 60 * 1000)))
    const triggerText = `${daysLeft} ${pluralize("day", daysLeft)}`
    let deadlineLabel = "Deadline to address this metric was"
    let trigger = <Label color="red">{triggerText}</Label>
    if (timeLeft >= 0) {
        deadlineLabel = "Time left to address this metric is"
        trigger = <span>{triggerText}</span>
    }
    return (
        <Popup flowing hoverable trigger={trigger}>
            <TimeAgoWithDate date={deadline}>{deadlineLabel}</TimeAgoWithDate>.<br/>
            You can configure the desired reaction times in the report header.
        </Popup>
    )
}
