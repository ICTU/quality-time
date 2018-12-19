import React from 'react';
import { Icon, Label, Table } from 'semantic-ui-react';

function Measurement(props) {
  const m = props.measurement;
  let measurement_text = '';
  let icon = '';
  if (m.measurement === null) {
    measurement_text = '? ' + m.unit;
    icon = <Icon color='red' name='exclamation triangle'/>;
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
        {m.source_responses.map((source_response) =>
          <Label as='a' tag>
            <a href={source_response.landing_url}>{m.source} </a>
            {icon}
        </Label>)}
      </Table.Cell>
    </Table.Row>
  )
}

export default Measurement;
