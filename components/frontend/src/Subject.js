import React, { Component } from 'react';
import { Button, Icon, Segment, Table } from 'semantic-ui-react';
import Metric from './Metric.js';
import { SubjectTitleContainer } from './SubjectTitle.js';

class Subject extends Component {
  onAddMetric(event) {
    event.preventDefault();
    const self = this;
    fetch(`${window.server_url}/report/${this.props.report.report_uuid}/subject/${this.props.subject_uuid}/metric`, {
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
    const subject = this.props.report.subjects[this.props.subject_uuid];
    const metrics = Object.keys(subject.metrics).map((metric_uuid) =>
      <Metric
        datamodel={this.props.datamodel}
        key={metric_uuid}
        metric_uuid={metric_uuid}
        nr_new_measurements={this.props.nr_new_measurements}
        readOnly={this.props.readOnly}
        reload={this.props.reload}
        report={this.props.report}
        report_date={this.props.report_date}
        search_string={this.props.search_string}
        subject_uuid={this.props.subject_uuid}
      />
    );
    return (
      <Segment basic>
        <SubjectTitleContainer report_uuid={this.props.report.report_uuid} subject_uuid={this.props.subject_uuid}
          subject={subject} reload={this.props.reload} readOnly={this.props.readOnly} />
        <Table>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell />
              <Table.HeaderCell>Metric</Table.HeaderCell>
              <Table.HeaderCell width="2">Trend</Table.HeaderCell>
              <Table.HeaderCell>Status</Table.HeaderCell>
              <Table.HeaderCell>Measurement</Table.HeaderCell>
              <Table.HeaderCell>Target</Table.HeaderCell>
              <Table.HeaderCell>Source</Table.HeaderCell>
              <Table.HeaderCell>Comment</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>{metrics}</Table.Body>
          {!this.props.readOnly &&
            <Table.Footer>
              <Table.Row>
                <Table.HeaderCell colSpan='8'>
                  <Button floated='left' icon primary basic onClick={(e) => this.onAddMetric(e)}>
                    <Icon name='plus' /> Add metric
                </Button>
                </Table.HeaderCell>
              </Table.Row>
            </Table.Footer>}
        </Table>
      </Segment>
    )
  }
}

export { Subject };
