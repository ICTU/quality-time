import React from 'react';
import { Label, Popup } from 'semantic-ui-react';


function SourceStatus(props) {
  const source_type = props.metric["sources"][props.source_uuid]["type"];
  const source_name = props.datamodel["sources"][source_type]["name"];
  if (props.source.connection_error || props.source.parse_error) {
    return (
      <Popup
        wide='very'
        content={props.source.connection_error ? props.source.connection_error : props.source.parse_error}
        header={props.source.connection_error ? 'Connection error' : 'Parse error'}
        trigger={<Label color='red' tabIndex="0"><a href={props.source.landing_url}>{source_name}</a></Label>} />)
  } else {
    return (
      <Label tabIndex="0">
        <a href={props.source.landing_url}>{source_name}</a>
      </Label>
    )
  }
}

export { SourceStatus };
