import React from 'react';
import { Label, Popup } from 'semantic-ui-react';


function SourceStatus(props) {
  if (props.source.connection_error || props.source.parse_error) {
    return (
      <Popup
        wide='very'
        content={props.source.connection_error ? props.source.connection_error : props.source.parse_error}
        header={props.source.connection_error ? 'Connection error' : 'Parse error'}
        trigger={<Label color='red' tabIndex="0"><a href={props.source.landing_url}>{props.source.name}</a></Label>} />)
  } else {
    return (
      <Label tabIndex="0">
        <a href={props.source.landing_url}>{props.source.name}</a>
      </Label>
    )
  }
}

export { SourceStatus };
