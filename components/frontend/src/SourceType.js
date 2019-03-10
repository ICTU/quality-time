import React from 'react';
import { SingleChoiceParameter } from './SingleChoiceParameter.js';

function SourceType(props) {
  let options = [];
  props.datamodel.metrics[props.metric_type].sources.forEach(
    (key) => { options.push({ text: props.datamodel.sources[key].name, value: key }) });
  return (
    <SingleChoiceParameter parameter_key="type" parameter_name="Source type" parameter_value={props.source_type}
      parameter_values={options} set_parameter={props.set_source_attribute} readOnly={props.readOnly} />
  )
}

export { SourceType };
