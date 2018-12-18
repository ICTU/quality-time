import React from 'react';
import { Statistic, StatisticValue, StatisticLabel, Table } from 'semantic-ui-react';

function Measurement(props) {
  const m = props.measurement;
  if (m) {
    return (
      <Table.Row>
        <Table.Cell>
          <Statistic horizontal size='mini' color={m.status === "target_met" ? "green" : "red"}>
            <StatisticValue>{m.measurement === null ? "?" : m.measurement}</StatisticValue>
            <StatisticLabel>{m.unit}</StatisticLabel>
          </Statistic>
        </Table.Cell>
        <Table.Cell>
          <Statistic horizontal size='mini'>
            <StatisticValue>{m.target}</StatisticValue>
            <StatisticLabel>{m.unit}</StatisticLabel>
          </Statistic>
        </Table.Cell>
      </Table.Row>
    )
  } else {
    return (
      <div>Measurement: unknown</div>
    )
  }
}

export default Measurement;
