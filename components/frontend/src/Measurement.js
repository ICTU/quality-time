import React from 'react';
import { Label, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';


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
  const metric = props.metric;
  const measurement = props.measurement;
  return (
    <Table.Row positive={measurement.status === "target_met"}
               negative={measurement.status === "target_not_met"}
               warning={measurement.status === null}>
      <Table.Cell>
        {metric.name}
      </Table.Cell>
      <Popup trigger={<Table.Cell>{(measurement.measurement === null ? '?' : measurement.measurement) + ' ' + metric.unit}</Table.Cell>} flowing hoverable>
        Measured <TimeAgo date={measurement.end} /> ({measurement.start} - {measurement.end})
      </Popup>
      <Table.Cell>
          {metric.direction} {measurement.target} {metric.unit}
      </Table.Cell>
      <Table.Cell>
        {props.source.responses.map((response) => <Source key={response.api_url} source={props.source.name} source_response={response} />)}
      </Table.Cell>
    </Table.Row>
  )
}

export default Measurement;
