import React from 'react';
import { Label, Popup } from '../semantic_ui_react_wrappers';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { pluralize } from '../utils';
import { metricReactionDeadline } from '../defaults';

export function TimeLeft({ status, statusStart }) {
    if (["target_met", "debt_target_met", "informative"].indexOf(status) >= 0 || !statusStart) {
        return null
    }
    let deadline = new Date(statusStart)
    deadline.setDate(deadline.getDate() + metricReactionDeadline[status])
    const now = new Date()
    const timeLeft = deadline.getTime() - now.getTime()
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
