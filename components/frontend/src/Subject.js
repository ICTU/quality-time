import React, { Component } from 'react';
import { Button, Icon, Segment, Table } from 'semantic-ui-react';
import Metric from './Metric.js';
import { SubjectTitle } from './SubjectTitle.js';

class Subject extends Component {
  onAddMetric(event) {
    event.preventDefault();
    const self = this;
    fetch(`${window.server_url}/report/${this.props.report.report_uuid}/subject/${this.props.subject_uuid}/metric/new`, {
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
        <SubjectTitle
          datamodel={this.props.datamodel}
          readOnly={this.props.readOnly}
          reload={this.props.reload}
          report_uuid={this.props.report.report_uuid}
          subject={subject}
          subject_uuid={this.props.subject_uuid}
        />
        <Table>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell />
              <Table.HeaderCell>Metric</Table.HeaderCell>
              <Table.HeaderCell width="2">Trend (7 days)</Table.HeaderCell>
              <Table.HeaderCell>Status</Table.HeaderCell>
              <Table.HeaderCell>Measurement</Table.HeaderCell>
              <Table.HeaderCell>Target</Table.HeaderCell>
              <Table.HeaderCell>Source</Table.HeaderCell>
              <Table.HeaderCell>Comment</Table.HeaderCell>
              <Table.HeaderCell>Tags</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>{metrics}</Table.Body>
          {!this.props.readOnly &&
            <Table.Footer>
              <Table.Row>
                <Table.HeaderCell colSpan='9'>
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
