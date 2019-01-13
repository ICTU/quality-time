import React from 'react';
import { Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { Comment } from './Comment';
import { Source } from './Source';
import { TrendSparkline } from './TrendSparkline';


function Measurement(props) {
  const last_measurement = props.measurements[props.measurements.length - 1];
  const metric_id = last_measurement.request.request_url;
  const metric = last_measurement.metric;
  const measurement = last_measurement.measurement;
  const source = last_measurement.source;
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
        <TrendSparkline measurements={props.measurements} />
      </Table.Cell>
      <Popup trigger={<Table.Cell>{(measurement.measurement === null ? '?' : measurement.measurement) + ' ' + metric.unit}</Table.Cell>} flowing hoverable>
        Measured <TimeAgo date={measurement.end} /> ({start.toLocaleString()} - {end.toLocaleString()})
      </Popup>
      <Table.Cell>
          {metric.direction} {measurement.target} {metric.unit}
      </Table.Cell>
      <Table.Cell>
        {source.responses.map((response) => <Source key={response.api_url} source={source.name} source_response={response} />)}
      </Table.Cell>
      <Table.Cell>
        <Comment metric_id={metric_id} comment={last_measurement.comment} key={end} />
      </Table.Cell>
    </Table.Row>
  )
}

export default Measurement;
