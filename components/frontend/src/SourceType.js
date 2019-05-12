import React from 'react';
import { Header } from 'semantic-ui-react';
import { Logo } from './logos/Logo';
import { SingleChoiceInput } from './fields/SingleChoiceInput';

function SourceType(props) {
  let options = [];
  props.datamodel.metrics[props.metric_type].sources.forEach(
    (key) => {
      const source_type = props.datamodel.sources[key];
      options.push(
        {
          key: key,
          text: props.datamodel.sources[key].name,
          value: key,
          content: <Header as="h4"><Header.Content><Logo logo={key} alt={source_type.name} />{source_type.name}<Header.Subheader>{source_type.description}</Header.Subheader></Header.Content></Header>
        })
    });
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
