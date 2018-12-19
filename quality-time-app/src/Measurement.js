import React from 'react';
import { Label, Table } from 'semantic-ui-react';

function Measurement(props) {
  const m = props.measurement;
  return (
    <Table.Row positive={m.status === "target_met"} negative={m.status === "target_not_met"}
                warning={m.status === null}>
      <Table.Cell>
        {m.metric}
      </Table.Cell>
      <Table.Cell>
          {m.measurement === null ? "?" : m.measurement} {m.unit}
      </Table.Cell>
      <Table.Cell>
          {m.direction} {m.target} {m.unit}
      </Table.Cell>
      <Table.Cell>
        {m.source_responses.map((source_response) =>
          <Label as='a' tag>
            <a href={source_response.landing_url}>{m.source}</a>
        </Label>)}
      </Table.Cell>
    </Table.Row>
  )
}

export default Measurement;
