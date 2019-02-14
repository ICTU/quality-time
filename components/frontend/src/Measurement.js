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

function Unit(props) {
  if (props.hide_ignored_units && props.ignored) {return null};
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
            onClick={(e) => props.ignore(e, props.unit.key)}>
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

  ignore(event, unit_key) {
    event.preventDefault();
    const self = this;
    fetch(`http://localhost:8080/report/${this.props.report_uuid}/source/${this.props.source.source_uuid}/unit/${unit_key}/hide`, {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    }).then(() => self.props.reload());
  }

  hide_ignored_units(event) {
    event.preventDefault();
    this.setState({ hide_ignored_units: !this.state.hide_ignored_units })
  }

  render() {
    if (!Array.isArray(this.props.source.data) || this.props.source.data.length === 0) {
      return null;
    }
    const report_source = this.props.metric["sources"][this.props.source.source_uuid];
    const source_type = report_source["type"];
    const unit_attributes = this.props.datamodel.sources[source_type].units[this.props.metric_type];
    const hidden_data = report_source.hidden_data || [];
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
    const rows = this.props.source.data.map((unit) =>
      <Unit key={unit.key} unit={unit} unit_attributes={unit_attributes}
        hide_ignored_units={this.state.hide_ignored_units} ignored={hidden_data.includes(unit.key)}
        ignore={(e, key) => this.ignore(e, key)} />);
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
    (props.measurement === null) ?
      null :
      <>
        {props.measurement.sources.map((source) => <SourceUnits key={source.source_uuid} source={source}
          datamodel={props.datamodel} metric={props.metric} metric_type={props.metric_type}
          reload={props.reload} report_uuid={props.report_uuid}
          fetch_measurement={props.fetch_measurement} metric_uuid={props.metric_uuid} />)}
      </>
  )
}
function MeasurementDetails(props) {
  return (
    <Table.Row>
      <Table.Cell colSpan="7">
        <Grid stackable columns={2}>
          <Grid.Row>
            <Grid.Column>
              <Sources report_uuid={props.report_uuid} metric_uuid={props.metric_uuid} sources={props.sources}
                metric_type={props.metric_type} datamodel={props.datamodel} reload={props.reload} />
              <Units measurement={props.measurement} datamodel={props.datamodel} metric={props.metric}
                metric_type={props.metric_type} fetch_measurement={props.fetch_measurement}
                reload={props.reload} metric_uuid={props.metric_uuid} measurements={props.measurements}
                report_uuid={props.report_uuid} />
            </Grid.Column>
            <Grid.Column>
              <TrendGraph measurements={props.measurements} unit={props.unit} />
            </Grid.Column>
          </Grid.Row>
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
      let nr_hidden = 0;
      Object.values(this.props.metric.sources).forEach((source) => { nr_hidden += (source.hidden_data && source.hidden_data.length) || 0 });
      value = latest_measurement.value - nr_hidden;
      start = new Date(latest_measurement.start);
      end = new Date(latest_measurement.end);
      measurement_timestring = latest_measurement.end;
    }
    const target = this.props.metric.target;
    const metric_direction = this.props.datamodel["metrics"][this.state.edited_metric_type]["direction"];
    let status = null;
    if (value != null) {
      if (metric_direction === ">=") {
        status = value >= target ? "target_met" : "target_not_met"
      } else if (metric_direction === "<=") {
        status = value <= target ? "target_met" : "target_not_met"
      } else {
        status = value === target ? "target_met" : "target_not_met"
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
                {(value === null ? '?' : value) + ' ' + metric_unit}
              </Table.Cell>
            }
            flowing hoverable>
            Measured <TimeAgo date={measurement_timestring} /> ({start.toLocaleString()} - {end.toLocaleString()})
        </Popup>
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
          report_uuid={this.props.report_uuid}
          metric_uuid={this.props.metric_uuid} measurement={latest_measurement}
          metric={this.props.metric} fetch_measurement={this.props.fetch_measurement}
          metric_type={this.state.edited_metric_type} sources={this.props.metric.sources} />}
      </>
    )
  }
}

export default Measurement;
