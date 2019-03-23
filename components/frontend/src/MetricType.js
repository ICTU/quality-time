import React from 'react';
import { SingleChoiceInput } from './fields/SingleChoiceInput';

function MetricType(props) {
  let options = [];
  Object.keys(props.datamodel.metrics).forEach(
    (key) => { options.push({ key: key, text: props.datamodel.metrics[key].name, value: key }) });
  return (
    <SingleChoiceInput
      label="Metric type"
      options={options}
      readOnly={props.readOnly}
      set_value={(value) => props.set_metric_attribute("type", value)}
      value={props.metric_type}
    />
  )
}

export { MetricType };
