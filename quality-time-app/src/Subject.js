import React from 'react';
import { Header, Table, Segment } from 'semantic-ui-react';
import Metric from './Metric.js';

function Subject(props) {
  return (
    <Segment basic>
      <Header as='h2'>{props.title}</Header>
      <Table columns={2}>
          <Table.Header>
              <Table.Row>
                <Table.HeaderCell>Measurement</Table.HeaderCell>
                <Table.HeaderCell>Target</Table.HeaderCell>
              </Table.Row>
          </Table.Header>
          <Table.Body>
            {props.metrics.map((metric) => <Metric key={metric} metric={metric} />)}
          </Table.Body>
      </Table>
    </Segment>
  )
}

export { Subject };
