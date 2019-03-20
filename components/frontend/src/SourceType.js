import React from 'react';
import { SingleChoiceParameter } from './SingleChoiceParameter.js';

function SourceType(props) {
  let options = [];
  props.datamodel.metrics[props.metric_type].sources.forEach(
    (key) => { options.push({ text: props.datamodel.sources[key].name, value: key }) });
  return (
    <SingleChoiceParameter
      label="Source type"
      parameter_key="type"
      parameter_value={props.source_type}
      parameter_values={options}
      readOnly={props.readOnly}
      set_parameter={props.set_source_attribute}
    />
  )
}

export { SourceType };
