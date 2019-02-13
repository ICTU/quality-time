import React, { Component } from 'react';
import { Button, Icon, Segment, Table } from 'semantic-ui-react';
import Metric from './Metric.js';
import { SubjectTitleContainer } from './SubjectTitle.js';

class Subject extends Component {
  onAddMetric(event) {
    event.preventDefault();
    const self = this;
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/subject/${this.props.subject_uuid}/metric`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }).then(
      () => self.props.reload()
    );
  }
  render() {
    const metrics = Object.keys(this.props.subject.metrics).map((metric_uuid) =>
      <Metric key={metric_uuid} report_uuid={this.props.report_uuid} metric_uuid={metric_uuid}
        metric={this.props.subject.metrics[metric_uuid]} metric_type={this.props.subject.metrics[metric_uuid]["type"]}
        datamodel={this.props.datamodel} search_string={this.props.search_string} report_date={this.props.report_date}
        nr_new_measurements={this.props.nr_new_measurements} reload={this.props.reload} />);
    return (
      <Segment basic>
        <SubjectTitleContainer report_uuid={this.props.report_uuid} subject_uuid={this.props.subject_uuid}
           subject={this.props.subject} reload={this.props.reload} />
        <Table columns={7}>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell width={2}>Metric</Table.HeaderCell>
              <Table.HeaderCell width={2}>Trend</Table.HeaderCell>
              <Table.HeaderCell width={3}>Measurement</Table.HeaderCell>
              <Table.HeaderCell width={3}>Target</Table.HeaderCell>
              <Table.HeaderCell width={3}>Source</Table.HeaderCell>
              <Table.HeaderCell width={3}>Comment</Table.HeaderCell>
              <Table.HeaderCell width={1} />
            </Table.Row>
          </Table.Header>
          <Table.Body>{metrics}</Table.Body>
          <Table.Footer>
            <Table.Row>
              <Table.HeaderCell colSpan='7'>
                <Button floated='right' icon labelPosition='left' primary size='small'
                  onClick={(e) => this.onAddMetric(e)}>
                  <Icon name='plus' /> Add metric
                </Button>
              </Table.HeaderCell>
            </Table.Row>
          </Table.Footer>
        </Table>
      </Segment>
    )
  }
}

export { Subject };
