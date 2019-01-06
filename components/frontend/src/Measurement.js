import React from 'react';
import { Label, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { LineChart, Line } from 'recharts';


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
  const start = new Date(measurement.start);
  const end = new Date(measurement.end);
  return (
    <Table.Row positive={measurement.status === "target_met"}
               negative={measurement.status === "target_not_met"}
               warning={measurement.status === null}>
      <Table.Cell>
        {metric.name}
      </Table.Cell>
      <Table.Cell>
        <LineChart width={100} height={40} data={[{m:4},{m:5},{m:6},{m:4},{m:3},{m:6},{m:5}]}>
          <Line type="monotone" dataKey="m" />
        </LineChart>
      </Table.Cell>
      <Popup trigger={<Table.Cell>{(measurement.measurement === null ? '?' : measurement.measurement) + ' ' + metric.unit}</Table.Cell>} flowing hoverable>
        Measured <TimeAgo date={measurement.end} /> ({start.toLocaleString()} - {end.toLocaleString()})
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
