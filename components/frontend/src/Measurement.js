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

class SourceUnits extends Component {
  hide(event, unit_key) {
    event.preventDefault();
    let self = this;
    fetch(`http://localhost:8080/report/source/${this.props.source.source_uuid}/unit/${unit_key}/hide`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }).then(() => this.props.reload())
  }

  render() {
    if (!this.props.source.units || this.props.source.units.length === 0) {
      return null;
    }
    const report_source = this.props.metric["sources"][this.props.source.source_uuid];
    const source_type = report_source["type"];
    const unit_attributes = this.props.datamodel.sources[source_type].units[this.props.metric_type];
    const units = this.props.source.units.filter((unit) => !(report_source.hidden_units && report_source.hidden_units.includes(unit.key)));
    const headers =
      <Table.Row>
        {unit_attributes.map((unit_attribute) => <Table.HeaderCell key={unit_attribute.key}>{unit_attribute.name}</Table.HeaderCell>)}
        <Table.HeaderCell collapsing></Table.HeaderCell>
      </Table.Row>
    const rows = units.map((unit, row_index) =>
      <Table.Row key={row_index}>
        {unit_attributes.map((unit_attribute, col_index) =>
          <Table.Cell key={col_index}>
            {unit[unit_attribute.url] ? <a href={unit[unit_attribute.url]}>{unit[unit_attribute.key]}</a> : unit[unit_attribute.key]}
          </Table.Cell>)
        }
        <Table.Cell collapsing>
          <Button floated='right' icon primary size='small' basic
            onClick={(e) => this.hide(e, unit.key)}>
            <Icon name='hide' />
          </Button>
        </Table.Cell>
      </Table.Row>)
    return (
      <Table size='small'>
        <Table.Header>
          {headers}
        </Table.Header>
        <Table.Body>
          {rows}
        </Table.Body>
      </Table>
    )
  }
}

function Units(props) {
  return (
    <>
      {props.measurement.sources.map((source) => <SourceUnits key={source.source_uuid} source={source}
        datamodel={props.datamodel} metric={props.metric} metric_type={props.metric_type}
        reload={props.reload} />)}
    </>
  )
}
function MeasurementDetails(props) {
  return (
    <Table.Row>
      <Table.Cell colSpan="7">
        <Grid stackable columns={2}>
          <Grid.Column>
            <Sources metric_uuid={props.metric_uuid} sources={props.sources}
              metric_type={props.metric_type} datamodel={props.datamodel} reload={props.reload} />
            <Units measurement={props.measurement} datamodel={props.datamodel} metric={props.metric}
              metric_type={props.metric_type} reload={props.reload} />
          </Grid.Column>
          <Grid.Column>
            <TrendGraph measurements={props.measurements} unit={props.unit} />
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
    fetch(`http://localhost:8080/report/metric/${this.props.metric_uuid}/type`, {
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
    fetch(`http://localhost:8080/report/metric/${this.props.metric_uuid}`, {
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
    let measurement_value = null;
    sources.forEach((source) => {
      if (source.measurement === null) {
        measurement_value = null;
        return;
      }
      measurement_value += Number(source.measurement);
      const hidden_units = this.props.metric["sources"][source.source_uuid].hidden_units;
      const nr_hidden_units = hidden_units ? hidden_units.length : 0;
      measurement_value -= nr_hidden_units;
    });
    const start = new Date(measurement.start);
    const end = new Date(measurement.end);
    const target = this.props.metric.target;
    const metric_direction = this.props.datamodel["metrics"][this.state.edited_metric_type]["direction"];
    let status = null;
    if (measurement_value!= null) {
      if (metric_direction === ">=") {
        status = measurement_value >= target ? "target_met" : "target_not_met"
      } else if (metric_direction === "<=") {
        status = measurement_value <= target ? "target_met" : "target_not_met"
      } else {
        status = measurement_value === target ? "target_met" : "target_not_met"
      }
    }
    const positive = status === "target_met";
    const negative = status === "target_not_met";
    const warning = status === null;
    const metric_unit = this.props.datamodel["metrics"][this.state.edited_metric_type]["unit"];
    return (
      <>
        <Table.Row positive={positive} negative={negative} warning={warning}>
          <Table.Cell>
            <Icon size='large' name={this.state.show_details ? "caret down" : "caret right"} onClick={(e) => this.onExpand(e)}
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
                {(measurement_value === null ? '?' : measurement_value) + ' ' + metric_unit}
              </Table.Cell>
            }
            flowing hoverable>
            Measured <TimeAgo date={measurement.end} /> ({start.toLocaleString()} - {end.toLocaleString()})
        </Popup>
          <Table.Cell>
            <Target metric_uuid={this.props.metric_uuid}
              unit={metric_unit} direction={metric_direction} reload={this.props.reload}
              editable={this.state.hover} target={target} key={end} onEdit={this.props.onEdit} />
          </Table.Cell>
          <Table.Cell>
            {sources.map((source) => <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
              metric={this.props.metric} source={source} datamodel={this.props.datamodel} />)}
          </Table.Cell>
          <Table.Cell>
            <Comment metric_uuid={this.props.metric_uuid} comment={this.props.metric.comment} key={end} />
          </Table.Cell>
          <Table.Cell collapsing>
            <Button floated='right' icon primary size='small' negative basic
              onClick={(e) => this.delete_metric(e)}>
              <Icon name='trash alternate' />
            </Button>
          </Table.Cell>
        </Table.Row>
        {this.state.show_details && <MeasurementDetails measurements={this.props.measurements}
          unit={metric_unit} datamodel={this.props.datamodel} reload={this.props.reload}
          metric_uuid={this.props.metric_uuid} measurement={last_measurement}
          metric={this.props.metric}
          metric_type={this.state.edited_metric_type} sources={this.props.metric.sources} />}
      </>
    )
  }
}

export default Measurement;
