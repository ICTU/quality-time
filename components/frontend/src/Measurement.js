import React, { Component } from 'react';
import { Button, Grid, Icon, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { Comment } from './Comment';
import { SourceStatus } from './SourceStatus';
import { Target } from './Target';
import { TrendGraph } from './TrendGraph';
import { TrendSparkline } from './TrendSparkline';
import { Sources } from './Sources';
import { MetricType } from './MetricType';

function MeasurementDetails(props) {
  return (
    <Table.Row>
      <Table.Cell colSpan="7">
        <Grid stackable columns={2}>
          <Grid.Column>
            <TrendGraph measurements={props.measurements} unit={props.unit} />
          </Grid.Column>
          <Grid.Column>
            <Sources subject_uuid={props.subject_uuid} metric_uuid={props.metric_uuid} sources={props.sources}
              metric_type={props.metric_type} datamodel={props.datamodel} reload={props.reload} />
          </Grid.Column>
        </Grid>
      </Table.Cell>
    </Table.Row>
  )
}

class Measurement extends Component {
  constructor(props) {
    super(props);
    this.state = { show_details: false, edited_metric_type: props.metric_type }
  }
  post_metric_type(metric_type) {
    this.setState({ edited_metric_type: metric_type });
    fetch(`http://localhost:8080/report/subject/${this.props.subject_uuid}/metric/${this.props.metric_uuid}/type`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type: metric_type })
    });
  }
  reset_metric_type() {
    this.setState({ edited_metric_type: this.props.metric_type });
  }
  onExpand(event) {
    this.setState((state) => ({ show_details: !state.show_details }));
  }
  delete_metric(event) {
    event.preventDefault();
    const self = this;
    fetch(`http://localhost:8080/report/subject/${this.props.subject_uuid}/metric/${this.props.metric_uuid}`, {
      method: 'delete',
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
    const last_measurement = this.props.measurements[this.props.measurements.length - 1];
    const measurement = last_measurement.measurement;
    const sources = last_measurement.sources;
    const start = new Date(measurement.start);
    const end = new Date(measurement.end);
    const target = this.props.metric.target;
    const metric_direction = this.props.datamodel["metrics"][this.state.edited_metric_type]["direction"];
    let status = null;
    if (metric_direction === ">=") {
      status = measurement >= target ? "target_met" : "target_not_met"
    } else if (metric_direction === "<=") {
      status = measurement <= target ? "target_met" : "target_not_met"
    } else {
      status = measurement === target ? "target_met" : "target_not_met"
    }
    const positive = status === "target_met";
    const negative = status === "target_not_met";
    const warning = status === null;
    const metric_unit = this.props.datamodel["metrics"][this.state.edited_metric_type]["unit"];
    return (
      <>
        <Table.Row positive={positive} negative={negative} warning={warning}>
          <Table.Cell>
            <Icon name={this.state.show_details ? "caret down" : "caret right"} onClick={(e) => this.onExpand(e)}
              onKeyPress={(e) => this.onExpand(e)} tabIndex="0" />
            <MetricType post_metric_type={(m) => this.post_metric_type(m)}
              reset_metric_type={() => this.reset_metric_type()} datamodel={this.props.datamodel}
              metric_type={this.state.edited_metric_type} />
          </Table.Cell>
          <Table.Cell>
            <TrendSparkline measurements={this.props.measurements} />
          </Table.Cell>
          <Popup
            trigger={
              <Table.Cell>
                {(measurement.measurement === null ? '?' : measurement.measurement) + ' ' + metric_unit}
              </Table.Cell>
            }
            flowing hoverable>
            Measured <TimeAgo date={measurement.end} /> ({start.toLocaleString()} - {end.toLocaleString()})
        </Popup>
          <Table.Cell>
            <Target subject_uuid={this.props.subject_uuid} metric_uuid={this.props.metric_uuid}
              unit={metric_unit} direction={metric_direction} reload={this.props.reload}
              editable={this.state.hover} target={target} key={end} onEdit={this.props.onEdit} />
          </Table.Cell>
          <Table.Cell>
            {sources.map((source) => <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
              metric={this.props.metric} source={source} datamodel={this.props.datamodel} />)}
          </Table.Cell>
          <Table.Cell>
            <Comment subject_uuid={this.props.subject_uuid} metric_uuid={this.props.metric_uuid} comment={this.props.metric.comment} key={end} />
          </Table.Cell>
          <Table.Cell collapsing>
            <Button floated='right' icon primary size='small' negative
              onClick={(e) => this.delete_metric(e)}>
              <Icon name='trash alternate' />
            </Button>
          </Table.Cell>
        </Table.Row>
        {this.state.show_details && <MeasurementDetails measurements={this.props.measurements}
          unit={metric_unit} datamodel={this.props.datamodel} reload={this.props.reload}
          subject_uuid={this.props.subject_uuid} metric_uuid={this.props.metric_uuid}
          metric_type={this.state.edited_metric_type} sources={this.props.metric.sources} />}
      </>
    )
  }
}

export default Measurement;
