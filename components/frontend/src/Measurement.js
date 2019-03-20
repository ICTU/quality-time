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
    const status_icon = {target_met: 'smile', debt_target_met: 'money', target_not_met: 'frown', null: 'question'}[status];
    const metric = this.props.report.subjects[this.props.subject_uuid].metrics[this.props.metric_uuid];
    const target = metric.accept_debt ? metric.debt_target : metric.target;
    const metric_direction = this.props.datamodel.metrics[metric.type].direction;
    const positive = status === "target_met";
    const active = status === "debt_target_met";
    const negative = status === "target_not_met";
    const warning = status === null;
    const metric_unit = metric.unit || this.props.datamodel.metrics[metric.type].unit;
    const metric_name = metric.name || this.props.datamodel.metrics[metric.type].name;
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
            {metric_direction} {target} {metric_unit} {metric.accept_debt ? "(debt)" : ""}
          </Table.Cell>
          <Table.Cell>
            {sources.map((source) => <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
              metric={metric} source={source} datamodel={this.props.datamodel} />)}
          </Table.Cell>
          <Table.Cell>
            {metric.comment}
          </Table.Cell>
          <Table.Cell>
            {metric.comment}
          </Table.Cell>
        </Table.Row>
        {this.state.show_details &&
          <MeasurementDetails
            datamodel={this.props.datamodel}
            ignore_unit={this.props.ignore_unit}
            measurement={latest_measurement}
            measurements={this.props.measurements}
            metric_uuid={this.props.metric_uuid}
            readOnly={this.props.readOnly}
            reload={this.props.reload}
            report={this.props.report}
            set_metric_attribute={this.props.set_metric_attribute}
            subject_uuid={this.props.subject_uuid}
            unit={metric_unit}
          />}
      </>
    )
  }
}

export default Measurement;
