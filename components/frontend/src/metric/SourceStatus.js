import React from 'react';
import { Label, Popup } from 'semantic-ui-react';

export function SourceStatus(props) {
  // Source may be deleted from report but still referenced in the latest measurement, be prepared:
  if (!Object.keys(props.metric.sources).includes(props.source_uuid)) {return null}
  const source = props.metric.sources[props.source_uuid];
  const source_name = source.name || props.datamodel.sources[source.type].name;
  function source_label() {
    return (props.source.landing_url ? <a href={props.source.landing_url}>{source_name}</a> : source_name)
  }
  if (props.source.connection_error || props.source.parse_error) {
    return (
      <Popup
        flowing hoverable
        trigger={<Label color='red'>{source_label()}</Label>}>
          {props.source.connection_error ? 'Connection error' : 'Parse error'}
      </Popup>
    )
  } else {
    return source_label()
  }
}
