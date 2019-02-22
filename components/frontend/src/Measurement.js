import React, { Component } from 'react';
import { Button, Icon, Menu, Label, Tab, Table, Popup } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { Comment } from './Comment';
import { SourceStatus } from './SourceStatus';
import { Target } from './Target';
import { TrendGraph } from './TrendGraph';
import { TrendSparkline } from './TrendSparkline';
import { Sources } from './Sources';
import { MetricName } from './MetricName';
import { MetricType } from './MetricType';

function Unit(props) {
  if (props.hide_ignored_units && props.ignored) { return null };
  const style = props.ignored ? { textDecoration: "line-through" } : {};
  const icon = props.ignored ? 'toggle off' : 'toggle on';
  const help = props.ignored ? 'Stop ignoring' : 'Start ignoring';
  return (
    <Table.Row key={props.unit.key} style={style}>
      {props.unit_attributes.map((unit_attribute, col_index) =>
        <Table.Cell key={col_index}>
          {props.unit[unit_attribute.url] ?
            <a href={props.unit[unit_attribute.url]}>{props.unit[unit_attribute.key]}</a> :
            props.unit[unit_attribute.key]}
        </Table.Cell>)
      }
      <Table.Cell collapsing>
        <Popup trigger={
          <Button floated='right' icon primary size='small' basic
            onClick={(e) => props.ignore_unit(e, props.source_uuid, props.unit.key)}>
            <Icon name={icon} />
          </Button>} content={help} />
      </Table.Cell>
    </Table.Row>
  )
}

class SourceUnits extends Component {
  constructor(props) {
    super(props);
    this.state = { hide_ignored_units: false };
  }

  hide_ignored_units(event) {
    event.preventDefault();
    this.setState({ hide_ignored_units: !this.state.hide_ignored_units })
  }

  render() {
    if (!Array.isArray(this.props.source.units) || this.props.source.units.length === 0) {
      return null;
    }
    const report_source = this.props.metric["sources"][this.props.source.source_uuid];
    const source_type = report_source["type"];
    const unit_attributes = this.props.datamodel.sources[source_type].units[this.props.metric_type];
    const ignored_units = this.props.source.ignored_units || [];
    const headers =
      <Table.Row>
        {unit_attributes.map((unit_attribute) => <Table.HeaderCell key={unit_attribute.key}>{unit_attribute.name}</Table.HeaderCell>)}
        <Table.HeaderCell collapsing>
          <Popup trigger={
            <Button floated='right' icon primary size='small' basic
              onClick={(e) => this.hide_ignored_units(e)}>
              <Icon name={this.state.hide_ignored_units ? 'unhide' : 'hide'} />
            </Button>} content={this.state.hide_ignored_units ? 'Show ignored items' : 'Hide ignored items'} />
        </Table.HeaderCell>
      </Table.Row>
    const rows = this.props.source.units.map((unit) =>
      <Unit key={unit.key} unit={unit} unit_attributes={unit_attributes} source_uuid={this.props.source.source_uuid}
        hide_ignored_units={this.state.hide_ignored_units} ignored={ignored_units.includes(unit.key)}
        ignore_unit={this.props.ignore_unit} />);
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
  if (props.measurement == null) { return null };
  let panes = [];
  props.measurement.sources.forEach((source) => {
    const report_source = props.metric["sources"][source.source_uuid];
    const source_type = report_source.type;
    const source_name = report_source.name || props.datamodel["sources"][source_type]["name"];
    let nr_units = source.value || 0;
    const nr_units_displayed = (source.units && source.units.length) || 0;
    if (Number(nr_units) !== Number(nr_units_displayed)) { nr_units = `${nr_units_displayed} of ${nr_units}` };
    panes.push({
      menuItem: (<Menu.Item>{source_name}<Label>{nr_units}</Label></Menu.Item>),
      render: () => <Tab.Pane>
        <SourceUnits key={source.source_uuid} source={source}
          datamodel={props.datamodel} metric={props.metric} metric_type={props.metric_type}
          ignore_unit={props.ignore_unit} report_uuid={props.report_uuid} metric_uuid={props.metric_uuid} />
      </Tab.Pane>
    })
  });
  return (
    <Tab panes={panes} />
  )
}

function MeasurementDetails(props) {
  const unit_name = props.unit.charAt(0).toUpperCase() + props.unit.slice(1);
  const panes = [
    {
      menuItem: 'Sources', render: () => <Tab.Pane>
        <Sources report_uuid={props.report_uuid} metric_uuid={props.metric_uuid} sources={props.sources}
          metric_type={props.metric_type} datamodel={props.datamodel} reload={props.reload} />
      </Tab.Pane>
    }
  ];
  if (props.measurement) {
    panes.push(
      {
        menuItem: 'Trend', render: () => <Tab.Pane>
          <TrendGraph measurements={props.measurements} unit={unit_name} />
        </Tab.Pane>
      });
    const nr_units = props.measurement.sources.reduce((nr_units, source) => nr_units + (source.units && source.units.length) || 0, 0);
    if (nr_units > 0) {
      panes.push({
        menuItem: unit_name, render: () => <Tab.Pane>
          <Units measurement={props.measurement} datamodel={props.datamodel} metric={props.metric}
            metric_type={props.metric_type} ignore_unit={props.ignore_unit} metric_uuid={props.metric_uuid}
            measurements={props.measurements} report_uuid={props.report_uuid} />
        </Tab.Pane>
      })
    }
  }
  return (
    <Table.Row>
      <Table.Cell colSpan="10">
        <Tab panes={panes} />
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
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}/type`, {
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
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/metric/${this.props.metric_uuid}`, {
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
    var latest_measurement, start, end, value, sources, measurement_timestring;
    if (this.props.measurements.length === 0) {
      latest_measurement = null;
      value = null;
      sources = [];
      start = new Date();
      end = new Date();
      measurement_timestring = end.toISOString();
    } else {
      latest_measurement = this.props.measurements[this.props.measurements.length - 1];
      sources = latest_measurement.sources;
      value = latest_measurement.value;
      start = new Date(latest_measurement.start);
      end = new Date(latest_measurement.end);
      measurement_timestring = latest_measurement.end;
    }
    const target = this.props.metric.target;
    const metric_direction = this.props.datamodel["metrics"][this.state.edited_metric_type]["direction"];
    let status = null;
    let status_icon = 'question';
    if (value != null) {
      if (metric_direction === ">=") {
        status = value >= target ? "target_met" : "target_not_met"
        status_icon = value >= target ? 'smile' : 'frown';
      } else if (metric_direction === "<=") {
        status = value <= target ? "target_met" : "target_not_met"
        status_icon = value <= target ? 'smile' : 'frown';
      } else {
        status = value === target ? "target_met" : "target_not_met"
        status_icon = value === target ? 'smile' : 'frown';
      }
    }
    const positive = status === "target_met";
    const negative = status === "target_not_met";
    const warning = status === null;
    const metric_unit = this.props.datamodel.metrics[this.state.edited_metric_type].unit;
    const metric_name = this.props.metric.name || this.props.datamodel.metrics[this.state.edited_metric_type].name;
    return (
      <>
        <Table.Row positive={positive} negative={negative} warning={warning}>
          <Table.Cell collapsing>
            <Icon size='large' name={this.state.show_details ? "caret down" : "caret right"} onClick={(e) => this.onExpand(e)}
              onKeyPress={(e) => this.onExpand(e)} tabIndex="0" />
          </Table.Cell>
          <Table.Cell>
            <MetricName name={metric_name} report_uuid={this.props.report_uuid} metric_uuid={this.props.metric_uuid} />
          </Table.Cell>
          <Table.Cell>
            <MetricType post_metric_type={(m) => this.post_metric_type(m)}
              reset_metric_type={() => this.reset_metric_type()} datamodel={this.props.datamodel}
              metric_type={this.state.edited_metric_type} />
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
            <Target report_uuid={this.props.report_uuid} metric_uuid={this.props.metric_uuid}
              unit={metric_unit} direction={metric_direction} reload={this.props.reload}
              editable={this.state.hover} target={target} key={end} onEdit={this.props.onEdit} />
          </Table.Cell>
          <Table.Cell>
            {sources.map((source) => <SourceStatus key={source.source_uuid} source_uuid={source.source_uuid}
              metric={this.props.metric} source={source} datamodel={this.props.datamodel} />)}
          </Table.Cell>
          <Table.Cell>
            <Comment report_uuid={this.props.report_uuid} metric_uuid={this.props.metric_uuid}
              comment={this.props.metric.comment} key={end} />
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
          report_uuid={this.props.report_uuid} metric_uuid={this.props.metric_uuid}
          measurement={latest_measurement} metric={this.props.metric}
          ignore_unit={this.props.ignore_unit}
          metric_type={this.state.edited_metric_type} sources={this.props.metric.sources} />}
      </>
    )
  }
}

export default Measurement;
