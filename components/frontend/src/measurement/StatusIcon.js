import React from 'react';
import { Icon } from 'semantic-ui-react';
import { Popup } from '../semantic_ui_react_wrappers';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { getStatusName } from '../utils'
import './StatusIcon.css';

export function StatusIcon({ status, status_start, size }) {
    status = status || "unknown";
    const icon_name = {
        target_met: 'check', near_target_met: 'warning', debt_target_met: 'money', target_not_met: 'bolt',
        informative: 'info', unknown: 'question'
    }[status];
    const statusName = getStatusName(status)
    const icon = <Icon aria-label={statusName} className={status} inverted circular name={icon_name} size={size} />;
    return (status_start ? <Popup trigger={icon} flowing hoverable><TimeAgoWithDate date={status_start}>{`${statusName} since`}</TimeAgoWithDate></Popup> : icon);
}
