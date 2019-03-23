import React from 'react';
import { SingleChoiceInput } from './fields/SingleChoiceInput';

function SourceType(props) {
  let options = [];
  props.datamodel.metrics[props.metric_type].sources.forEach(
    (key) => { options.push({ text: props.datamodel.sources[key].name, value: key }) });
  return (
    <SingleChoiceInput
      label="Source type"
      options={options}
      readOnly={props.readOnly}
      set_value={(value) => props.set_source_attribute("type", value)}
      value={props.source_type}
    />
  )
}

export { SourceType };
