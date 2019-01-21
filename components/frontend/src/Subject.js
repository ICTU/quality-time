import React from 'react';
import { Table, Segment } from 'semantic-ui-react';
import { SubjectTitleContainer } from './SubjectTitle.js';
import Metric from './Metric.js';

function Subject(props) {
  const metrics = props.metrics.map((metric) =>
    <Metric key={metric} metric={metric} search_string={props.search_string}
            report_date={props.report_date} nr_new_measurements={props.nr_new_measurements} />);
  return (
    <Segment basic>
      <SubjectTitleContainer subject_index={props.subject_index} />
      <Table columns={6}>
          <Table.Header>
              <Table.Row>
                <Table.HeaderCell>Metric</Table.HeaderCell>
                <Table.HeaderCell>Trend</Table.HeaderCell>
                <Table.HeaderCell>Measurement</Table.HeaderCell>
                <Table.HeaderCell>Target</Table.HeaderCell>
                <Table.HeaderCell>Source</Table.HeaderCell>
                <Table.HeaderCell>Comment</Table.HeaderCell>
              </Table.Row>
          </Table.Header>
          <Table.Body>{metrics}</Table.Body>
      </Table>
    </Segment>
  )
}

export { Subject };
