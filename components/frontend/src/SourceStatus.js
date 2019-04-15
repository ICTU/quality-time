import React from 'react';
import { Label, Popup } from 'semantic-ui-react';


function SourceStatus(props) {
  // Source may be deleted from report but still referenced in the latest measurement, be prepared:
  if (!Object.keys(props.metric.sources).includes(props.source_uuid)) {return null};
  const source = props.metric.sources[props.source_uuid];
  const source_name = source.name || props.datamodel["sources"][source.type]["name"];
  if (props.source.connection_error || props.source.parse_error) {
    return (
      <Popup
        flowing hoverable
        trigger={<Label color='red'><a href={props.source.landing_url}>{source_name}</a></Label>}>
          {props.source.connection_error ? 'Connection error' : 'Parse error'}
      </Popup>
    )
  } else {
    return (
        <a href={props.source.landing_url}>{source_name}</a>
    )
  }
}

export { SourceStatus };
