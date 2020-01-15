import React from 'react';
import { Icon } from 'semantic-ui-react';

export function StatusIcon({ status }) {
  const status_icon = {
    target_met: 'check', near_target_met: 'warning', debt_target_met: 'money',
    target_not_met: 'x', missing: 'question'
  }[status || 'missing'];
  return (
    <Icon size='large' name={status_icon} />
  )
}