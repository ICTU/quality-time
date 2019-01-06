import React from 'react';
import { Label, Popup } from 'semantic-ui-react';


function Source(props) {
  if (props.source_response.connection_error || props.source_response.parse_error) {
    return (
      <Popup
        wide='very'
        content={props.source_response.connection_error ? props.source_response.connection_error : props.source_response.parse_error}
        header={props.source_response.connection_error ? 'Connection error' : 'Parse error'}
        trigger={<Label color='red'><a href={props.source_response.landing_url}>{props.source}</a></Label>} />)
  } else {
    return (
      <Label>
        <a href={props.source_response.landing_url}>{props.source}</a>
      </Label>
    )
  }
}

export { Source };
