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
    let deadlineLabel = "Deadline to address this metric was"
    if (timeLeft >= 0) {
        daysLeft = Math.round(timeLeft / (24 * 60 * 60 * 1000))
        deadlineLabel = "Time left to address this metric"
    }
    return (
        <Popup
            flowing
            hoverable
            trigger={<span>{`${daysLeft} ${pluralize("day", daysLeft)}`}</span>}
        >
            <TimeAgoWithDate date={deadline}>{deadlineLabel}</TimeAgoWithDate>.
            Configure the deadlines in the report header.
        </Popup>
    )
}
