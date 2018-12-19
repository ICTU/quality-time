import React from 'react';
import { Table } from 'semantic-ui-react';

function Measurement(props) {
  const m = props.measurement;
  if (m === null) {return null};
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
    </Table.Row>
  )
}

export default Measurement;
