import React, { Component } from 'react';
import { Grid, Icon, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { Comment } from './Comment';
import { SourceStatus } from './SourceStatus';
import { Target } from './Target';
import { TrendGraph } from './TrendGraph';
import { TrendSparkline } from './TrendSparkline';
import { Sources } from './Sources';
import { MetricType} from './MetricType';

function MeasurementDetails(props) {
  return (
    <Table.Row>
      <Table.Cell colSpan="6">
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
  render() {
    const last_measurement = this.props.measurements[this.props.measurements.length - 1];
    const measurement = last_measurement.measurement;
    const sources = last_measurement.sources;
    const start = new Date(measurement.start);
    const end = new Date(measurement.end);
    const positive = measurement.status === "target_met";
    const negative = measurement.status === "target_not_met";
    const warning = measurement.status === null;
    const metric_unit = this.props.datamodel["metrics"][this.state.edited_metric_type]["unit"];
    const metric_direction = this.props.datamodel["metrics"][this.state.edited_metric_type]["direction"];
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
            <Target measurement_id={last_measurement["_id"]} unit={metric_unit} direction={metric_direction}
              editable={this.state.hover} target={measurement.target} key={end} onEdit={this.props.onEdit} />
          </Table.Cell>
          <Table.Cell>
            {sources.map((source) => <SourceStatus key={source.source_uuid} source={source} />)}
          </Table.Cell>
          <Table.Cell>
            <Comment measurement_id={last_measurement["_id"]} comment={last_measurement.comment} key={end} />
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
