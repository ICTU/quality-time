import React from 'react';
import { Icon, Popup } from 'semantic-ui-react';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import './StatusIcon.css';

export function StatusIcon({ status, status_start }) {
    const icon_name = {
        target_met: 'check', near_target_met: 'warning', debt_target_met: 'money', target_not_met: 'bolt',
        unknown: 'question'
    }[status || "unknown"];
    const status_name = {
        target_met: 'Target met', near_target_met: 'Near target met', debt_target_met: 'Debt target met',
        target_not_met: 'Target not met', unknown: 'Unknown'
    }[status || "unknown"];
    const icon = <Icon aria-label={status_name} className={status} inverted circular name={icon_name} />;
    return (status_start ? <Popup trigger={icon} flowing hoverable><TimeAgoWithDate date={status_start}>{`${status_name} since`}</TimeAgoWithDate></Popup> : icon);
}