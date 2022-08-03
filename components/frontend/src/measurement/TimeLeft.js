import React from 'react';
import { Popup } from '../semantic_ui_react_wrappers';
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
    let daysLeft = 0
    let deadlineLabel = "Deadline was"
    if (timeLeft >= 0) {
        daysLeft = Math.round(timeLeft / (24 * 60 * 60 * 1000))
        deadlineLabel = "Time left"
    }
    return (<Popup trigger={<span>{`${daysLeft} ${pluralize("day", daysLeft)}`}</span>} flowing hoverable><TimeAgoWithDate date={deadline}>{deadlineLabel}</TimeAgoWithDate></Popup>)
}
