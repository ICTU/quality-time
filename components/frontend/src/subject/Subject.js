import React, { Component } from 'react';
import { Button, Icon, Popup, Table } from 'semantic-ui-react';
import Metric from '../metric/Metric';
import { SubjectTitle } from './SubjectTitle';
import { add_metric } from '../api/metric';

class Subject extends Component {
  constructor(props) {
    super(props);
    this.state = { hide_metrics_not_requiring_action: false, sort_column: null, sort_direction: null, last_measurements: {} };
  }
  hide_metrics_not_requiring_action(event) {
    event.preventDefault();
    this.setState({ hide_metrics_not_requiring_action: !this.state.hide_metrics_not_requiring_action })
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
    const { hide_metrics_not_requiring_action, sort_column, sort_direction } = this.state;
    let metric_components = [];
    Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
      const status = (this.state.last_measurements[metric_uuid] && this.state.last_measurements[metric_uuid].status) || '';
      if (hide_metrics_not_requiring_action && (status === "target_met" || status === "debt_target_met")) { return }
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
    });
    if (sort_column !== null) {
      let self = this;
      const status_order = { "": "0", target_not_met: "1", debt_target_met: "2", near_target_met: "3", target_met: "4" };
      const sorters = {
        name: function (m1, m2) {
          const attribute1 = m1.props.metric.name || self.props.datamodel.metrics[m1.props.metric.type].name;
          const attribute2 = m2.props.metric.name || self.props.datamodel.metrics[m2.props.metric.type].name;
          return attribute1.localeCompare(attribute2)
        },
        measurement: function (m1, m2) {
          const attribute1 = (self.state.last_measurements[m1.props.metric_uuid] && self.state.last_measurements[m1.props.metric_uuid].value) || '';
          const attribute2 = (self.state.last_measurements[m2.props.metric_uuid] && self.state.last_measurements[m2.props.metric_uuid].value) || '';
          return attribute1.localeCompare(attribute2)
        },
        target: function (m1, m2) {
          const attribute1 = m1.props.metric.accept_debt ? m1.props.metric.debt_target : m1.props.metric.target;
          const attribute2 = m2.props.metric.accept_debt ? m2.props.metric.debt_target : m2.props.metric.target;
          return attribute1.localeCompare(attribute2)
        },
        comment: function (m1, m2) {
          const attribute1 = m1.props.metric.comment || '';
          const attribute2 = m2.props.metric.comment || '';
          return attribute1.localeCompare(attribute2)
        },
        status: function (m1, m2) {
          const attribute1 = status_order[(self.state.last_measurements[m1.props.metric_uuid] && self.state.last_measurements[m1.props.metric_uuid].status) || ''];
          const attribute2 = status_order[(self.state.last_measurements[m2.props.metric_uuid] && self.state.last_measurements[m2.props.metric_uuid].status) || ''];
          return attribute1.localeCompare(attribute2)
        },
        source: function (m1, m2) {
          let m1_sources = Object.values(m1.props.metric.sources).map((source) => source.name || self.props.datamodel.sources[source.type].name);
          m1_sources.sort();
          let m2_sources = Object.values(m2.props.metric.sources).map((source) => source.name || self.props.datamodel.sources[source.type].name);
          m2_sources.sort();
          const attribute1 = m1_sources.length > 0 ? m1_sources[0] : '';
          const attribute2 = m2_sources.length > 0 ? m2_sources[0] : '';
          return attribute1.localeCompare(attribute2)
        },
        tags: function (m1, m2) {
          let m1_tags = m1.props.metric.tags;
          m1_tags.sort();
          let m2_tags = m2.props.metric.tags;
          m2_tags.sort();
          const attribute1 = m1_tags.length > 0 ? m1_tags[0] : '';
          const attribute2 = m2_tags.length > 0 ? m2_tags[0] : '';
          return attribute1.localeCompare(attribute2)
        }
      }
      metric_components.sort(sorters[sort_column]);
      if (sort_direction === 'descending') {
        metric_components.reverse()
      }
    }
    return (
      <div id={this.props.subject_uuid}>
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
              <Table.HeaderCell collapsing textAlign="center">
                <Popup trigger={
                  <Button
                    basic
                    compact
                    icon={hide_metrics_not_requiring_action ? 'unhide' : 'hide'}
                    onClick={(e) => this.hide_metrics_not_requiring_action(e)}
                    primary
                  />
                } content={hide_metrics_not_requiring_action ? 'Show all metrics' : 'Hide metrics not requiring action'} />
              </Table.HeaderCell>
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
              <Table.HeaderCell
                onClick={(event) => this.handle_sort(event, 'measurement')}
                sorted={sort_column === 'measurement' ? sort_direction : null}
              >
                Measurement
              </Table.HeaderCell>
              <Table.HeaderCell
                onClick={(event) => this.handle_sort(event, 'target')}
                sorted={sort_column === 'target' ? sort_direction : null}
              >
                Target
              </Table.HeaderCell>
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
              <Table.HeaderCell
                onClick={(event) => this.handle_sort(event, 'tags')}
                sorted={sort_column === 'tags' ? sort_direction : null}
              >
                Tags
              </Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>{metric_components}</Table.Body>
          {!this.props.readOnly &&
            <Table.Footer>
              <Table.Row>
                <Table.HeaderCell colSpan='9'>
                  <Button
                    basic
                    floated='left'
                    icon
                    onClick={() => add_metric(this.props.report.report_uuid, this.props.subject_uuid, this.props.reload)}
                    primary
                  >
                    <Icon name='plus' /> Add metric
                  </Button>
                </Table.HeaderCell>
              </Table.Row>
            </Table.Footer>}
        </Table>
      </div>
    )
  }
}

export { Subject };
