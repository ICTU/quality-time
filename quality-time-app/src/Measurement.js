import React from 'react';
import { Label, Table, Popup } from 'semantic-ui-react';

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

function Measurement(props) {
  const m = props.measurement;
  let measurement_text = '';
  if (m.measurement === null) {
    measurement_text = '? ' + m.unit;
  } else {
    measurement_text = m.measurement + ' ' + m.unit;
  }
  return (
    <Table.Row positive={m.status === "target_met"} negative={m.status === "target_not_met"}
                warning={m.status === null}>
      <Table.Cell>
        {m.metric}
      </Table.Cell>
      <Table.Cell>
        {measurement_text}
      </Table.Cell>
      <Table.Cell>
          {m.direction} {m.target} {m.unit}
      </Table.Cell>
      <Table.Cell>
        {m.source_responses.map((source_response) => <Source source={m.source} source_response={source_response} />)}
      </Table.Cell>
    </Table.Row>
  )
}

export default Measurement;
