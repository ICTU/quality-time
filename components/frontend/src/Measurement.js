import React, { Component } from 'react';
import { Grid, Icon, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { Comment } from './Comment';
import { Source } from './Source';
import { Target } from './Target';
import { TrendGraph } from './TrendGraph';
import { TrendSparkline } from './TrendSparkline';
import { SourceTable } from './SourceTable';

function MeasurementDetails(props) {
  return (
    <Table.Row>
      <Table.Cell colSpan="6">
        <Grid stackable columns={2}>
          <Grid.Column>
            <TrendGraph measurements={props.measurements} unit={props.unit} />
          </Grid.Column>
          <Grid.Column>
            <SourceTable subject_index={props.subject_index} metric_index={props.metric_index} sources={props.sources} />
          </Grid.Column>
        </Grid>
      </Table.Cell>
    </Table.Row>
  )
}

class Measurement extends Component {
  constructor(props) {
    super(props);
    this.state = { show_details: false }
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
    return (
      <>
        <Table.Row positive={positive} negative={negative} warning={warning}>
          <Table.Cell>
            <Icon name={this.state.show_details ? "caret down" : "caret right"} onClick={(e) => this.onExpand(e)}
              onKeyPress={(e) => this.onExpand(e)} tabIndex="0" />
            {this.props.metric_type.name}
          </Table.Cell>
          <Table.Cell>
            <TrendSparkline measurements={this.props.measurements} />
          </Table.Cell>
          <Popup
            trigger={
              <Table.Cell>
                {(measurement.measurement === null ? '?' : measurement.measurement) + ' ' + this.props.metric_type.unit}
              </Table.Cell>
            }
            flowing hoverable>
            Measured <TimeAgo date={measurement.end} /> ({start.toLocaleString()} - {end.toLocaleString()})
        </Popup>
          <Table.Cell>
            <Target measurement_id={last_measurement["_id"]} metric_type={this.props.metric_type}
              editable={this.state.hover} target={measurement.target} key={end} onEdit={this.props.onEdit} />
          </Table.Cell>
          <Table.Cell>
            {sources.map((source) => <Source key={source.api_url} source={source} />)}
          </Table.Cell>
          <Table.Cell>
            <Comment measurement_id={last_measurement["_id"]} comment={last_measurement.comment} key={end} />
          </Table.Cell>
        </Table.Row>
        {this.state.show_details && <MeasurementDetails subject_index={this.props.subject_index}
          metric_index={this.props.metric_index} measurements={this.props.measurements}
          unit={this.props.metric_type.unit} sources={this.props.metric.sources} />}
      </>
    )
  }
}

export default Measurement;
