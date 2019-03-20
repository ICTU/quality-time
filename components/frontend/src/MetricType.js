import React from 'react';
import { SingleChoiceParameter } from './SingleChoiceParameter.js';

function MetricType(props) {
  let options = [];
  Object.keys(props.datamodel.metrics).forEach(
    (key) => { options.push({ text: props.datamodel.metrics[key].name, value: key }) });
  return (
    <SingleChoiceParameter
      label="Metric type"
      parameter_key="type"
      parameter_value={props.metric_type}
      parameter_values={options}
      readOnly={props.readOnly}
      set_parameter={props.set_metric_attribute}
    />
  )
}

export { MetricType };
