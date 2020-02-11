import React from 'react';
import { Icon } from 'semantic-ui-react';
import './StatusIcon.css';

export function StatusIcon({ status }) {
  const status_icon = {
    target_met: 'check', near_target_met: 'warning', debt_target_met: 'money', target_not_met: 'x',
    unknown: 'question'};
  return <Icon className={status} inverted circular size='large' name={status_icon[status || 'unknown']} />
}