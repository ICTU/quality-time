import React from 'react';
import { SingleChoiceParameter } from './SingleChoiceParameter.js';

function MetricType(props) {
  let options = [];
  Object.keys(props.datamodel.metrics).forEach(
    (key) => { options.push({ text: props.datamodel.metrics[key].name, value: key }) });
  return (
    <SingleChoiceParameter parameter_key="type" parameter_name="Metric type" parameter_value={props.metric_type}
      parameter_values={options} set_parameter={props.set_metric_attribute} readOnly={props.readOnly}
    />
  )
}

export { MetricType };
