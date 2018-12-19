import React from 'react';
import { Header, Table, Segment } from 'semantic-ui-react';
import Metric from './Metric.js';

function Subject(props) {
  const metrics = props.metrics.map((metric) =>
    <Metric key={metric} metric={metric} search_string={props.search_string} />);
  return (
    <Segment basic>
      <Header as='h2'>{props.title}</Header>
      <Table columns={3}>
          <Table.Header>
              <Table.Row>
                <Table.HeaderCell>Metric</Table.HeaderCell>
                <Table.HeaderCell>Measurement</Table.HeaderCell>
                <Table.HeaderCell>Target</Table.HeaderCell>
              </Table.Row>
          </Table.Header>
          <Table.Body>{metrics}</Table.Body>
      </Table>
    </Segment>
  )
}

export { Subject };
