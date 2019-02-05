import React from 'react';
import { Label, Popup } from 'semantic-ui-react';


function SourceStatus(props) {
  // Source may be deleted from report but still referenced in the latest measurement, be prepared:
  if (!Object.keys(props.metric.sources).includes(props.source_uuid)) {return null};
  const source_type = props.metric["sources"][props.source_uuid]["type"];
  const source_name = props.datamodel["sources"][source_type]["name"];
  if (props.source.connection_error || props.source.parse_error) {
    let content = props.source.connection_error ? props.source.connection_error : props.source.parse_error;
    return (
      <Popup
        wide='very' size='tiny' hoverable
        trigger={<Label color='red' tabIndex="0"><a href={props.source.landing_url}>{source_name}</a></Label>}>
        <Popup.Header>
          {props.source.connection_error ? 'Connection error' : 'Parse error'}
        </Popup.Header>
        <Popup.Content>
          {content.split(/[\r\n]/g).map((line) =>
            <div key={line}>{line.replace(/ {4}/, '>>> ').replace(/ {2}/g, '- ')}</div>)}
        </Popup.Content>
      </Popup>
    )
  } else {
    return (
      <Label tabIndex="0">
        <a href={props.source.landing_url}>{source_name}</a>
      </Label>
    )
  }
}

export { SourceStatus };
