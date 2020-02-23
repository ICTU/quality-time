import React from 'react';
import { Measurement } from './Measurement';
import { get_metric_name } from '../utils';

export function Metric(props) {
  const { search_string } = props;
  const metric = props.report.subjects[props.subject_uuid].metrics[props.metric_uuid];
  const metric_name = get_metric_name(metric, props.datamodel);
  if (search_string && !metric_name.toLowerCase().includes(search_string.toLowerCase())) { return null }
  return <Measurement {...props} />
}
