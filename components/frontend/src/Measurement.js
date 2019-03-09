import React, { Component } from 'react';
import { Icon, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { SourceStatus } from './SourceStatus';
import { TrendSparkline } from './TrendSparkline';
import { MeasurementDetails } from './MeasurementDetails';

class Measurement extends Component {
  constructor(props) {
    super(props);
    this.state = { show_details: false }
  }
  onExpand(event) {
    event.preventDefault();
    this.setState((state) => ({ show_details: !state.show_details }));
  }
  render() {
    var latest_measurement, start, end, value, status, sources, measurement_timestring;
    if (this.props.measurements.length === 0) {
      latest_measurement = null;
      value = null;
      status = null;
      sources = [];
      start = new Date();
      end = new Date();
      measurement_timestring = end.toISOString();
    } else {
      latest_measurement = this.props.measurements[this.props.measurements.length - 1];
      sources = latest_measurement.sources;
      value = latest_measurement.value;
      status = latest_measurement.status;
      start = new Date(latest_measurement.start);
      end = new Date(latest_measurement.end);
      measurement_timestring = latest_measurement.end;
    }
    const status_icon = {target_met: 'smile', target_not_met: 'frown', null: 'question'}[status];
    const target = this.props.metric.target;
    const metric_direction = this.props.datamodel.metrics[this.props.metric.type].direction;
    const positive = status === "target_met";
    const active = status === "debt_target_met";
    const negative = status === "target_not_met";
    const warning = status === null;
    const metric_unit = this.props.datamodel.metrics[this.props.metric.type].unit;
    const metric_name = this.props.metric.name || this.props.datamodel.metrics[this.props.metric.type].name;
    return (
      <>
        <Table.Row positive={positive} negative={negative} warning={warning} active={active}>
          <Table.Cell collapsing>
            <Icon size='large' name={this.state.show_details ? "caret down" : "caret right"} onClick={(e) => this.onExpand(e)}
              onKeyPress={(e) => this.onExpand(e)} tabIndex="0" />
          </Table.Cell>
          <Table.Cell>
            {metric_name}
          </Table.Cell>
          <Table.Cell>
            <TrendSparkline measurements={this.props.measurements} />
          </Table.Cell>
          <Table.Cell>
            <Icon size='large' name={status_icon} />
          </Table.Cell>
          <Table.Cell>
            <Popup
              trigger={<span>{(value === null ? '?' : value) + ' ' + metric_unit}</span>}
              flowing hoverable>
              Measured <TimeAgo date={measurement_timestring} /> ({start.toLocaleString()} - {end.toLocaleString()})
          </Popup>
          </Table.Cell>
          <Table.Cell>
            {metric_direction} {target} {metric_unit}
          </Table.Cell>
          <Table.Cell>
            {sources.map((source) => <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
              metric={this.props.metric} source={source} datamodel={this.props.datamodel} />)}
          </Table.Cell>
          <Table.Cell>
            {this.props.metric.comment}
          </Table.Cell>
        </Table.Row>
        {this.state.show_details && <MeasurementDetails measurements={this.props.measurements}
          unit={metric_unit} datamodel={this.props.datamodel} reload={this.props.reload}
          report_uuid={this.props.report_uuid} metric_uuid={this.props.metric_uuid}
          measurement={latest_measurement} metric={this.props.metric} user={this.props.user}
          set_metric_attribute={this.props.set_metric_attribute} ignore_unit={this.props.ignore_unit} />}
      </>
    )
  }
}

export default Measurement;
