import React, { Component } from 'react';
import { Button, Icon, Table } from 'semantic-ui-react';
import Metric from './Metric.js';
import { SubjectTitle } from './SubjectTitle.js';

class Subject extends Component {
  constructor(props) {
    super(props);
    this.state = { sort_column: null, sort_direction: null, last_measurements: {} };
  }

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

  handle_sort(event, column) {
    event.preventDefault();
    const sort_direction = this.state.sort_direction;
    this.setState(
      {
        sort_column: column,
        sort_direction: sort_direction === 'ascending' ? 'descending' : 'ascending'
      })
  }

  set_last_measurement(metric_uuid, last_measurement) {
    this.setState(prevState => (
      { last_measurements: { ...prevState.last_measurements, [metric_uuid]: last_measurement } }
    ));
  }

  render() {
    const subject = this.props.report.subjects[this.props.subject_uuid];
    const { sort_column, sort_direction } = this.state;
    let metric_components = [];
    Object.entries(subject.metrics).forEach(([metric_uuid, metric]) =>
      metric_components.push(
        <Metric
          datamodel={this.props.datamodel}
          key={metric_uuid}
          metric_uuid={metric_uuid}
          metric={metric}
          nr_new_measurements={this.props.nr_new_measurements}
          readOnly={this.props.readOnly}
          reload={this.props.reload}
          report={this.props.report}
          report_date={this.props.report_date}
          search_string={this.props.search_string}
          set_last_measurement={(m, l) => this.set_last_measurement(m, l)}
          subject_uuid={this.props.subject_uuid}
        />)
    );
    if (sort_column !== null) {
      let self = this;
      metric_components.sort(function (m1, m2) {
        if (sort_column === 'name') {
          const m1_name = m1.props.metric.name || self.props.datamodel.metrics[m1.props.metric.type].name;
          const m2_name = m2.props.metric.name || self.props.datamodel.metrics[m2.props.metric.type].name;
          return m1_name.localeCompare(m2_name);
        } else if (sort_column === 'comment') {
          const m1_comment = m1.props.metric.comment || '';
          const m2_comment = m2.props.metric.comment || '';
          return m1_comment.localeCompare(m2_comment);
        } else if (sort_column === 'status') {
          const m1_status = self.state.last_measurements[m1.props.metric_uuid].status || '';
          const m2_status = self.state.last_measurements[m2.props.metric_uuid].status || '';
          return m1_status < m2_status ? -1 : 1;
        } else if (sort_column === 'source') {
          let m1_sources = Object.values(m1.props.metric.sources).map((source) => source.name || self.props.datamodel.sources[source.type].name);
          m1_sources.sort();
          let m2_sources = Object.values(m2.props.metric.sources).map((source) => source.name || self.props.datamodel.sources[source.type].name);
          m2_sources.sort();
          const m1_source = m1_sources.length > 0 ? m1_sources[0] : '';
          const m2_source = m2_sources.length > 0 ? m2_sources[0] : '';
          return m1_source < m2_source ? -1 : 1;
        }
        return 0;
      });
      if (sort_direction === 'descending') {
        metric_components.reverse()
      }
    }
    return (
      <>
        <SubjectTitle
          datamodel={this.props.datamodel}
          readOnly={this.props.readOnly}
          reload={this.props.reload}
          report_uuid={this.props.report.report_uuid}
          subject={subject}
          subject_uuid={this.props.subject_uuid}
        />
        <Table sortable>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell />
              <Table.HeaderCell
                onClick={(event) => this.handle_sort(event, 'name')}
                sorted={sort_column === 'name' ? sort_direction : null}
              >
                Metric
              </Table.HeaderCell>
              <Table.HeaderCell width="2">Trend (7 days)</Table.HeaderCell>
              <Table.HeaderCell
                onClick={(event) => this.handle_sort(event, 'status')}
                sorted={sort_column === 'status' ? sort_direction : null}
              >
                Status
              </Table.HeaderCell>
              <Table.HeaderCell>Measurement</Table.HeaderCell>
              <Table.HeaderCell>Target</Table.HeaderCell>
              <Table.HeaderCell
                onClick={(event) => this.handle_sort(event, 'source')}
                sorted={sort_column === 'source' ? sort_direction : null}
              >
                Source
              </Table.HeaderCell>
              <Table.HeaderCell
                onClick={(event) => this.handle_sort(event, 'comment')}
                sorted={sort_column === 'comment' ? sort_direction : null}
              >
                Comment</Table.HeaderCell>
              <Table.HeaderCell>Tags</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>{metric_components}</Table.Body>
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
      </>
    )
  }
}

export { Subject };
