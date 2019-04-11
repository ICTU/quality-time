import React, { Component } from 'react';
import { Button, Grid, Icon, Menu, Label, Tab, Table, Popup, Radio } from 'semantic-ui-react';
import { TextInput } from './fields/TextInput';

function UnitAttribute(props) {
  let cell_contents = props.unit[props.unit_attribute.key];
  cell_contents = props.unit[props.unit_attribute.url] ? <a href={props.unit[props.unit_attribute.url]}>{cell_contents}</a> : cell_contents;
  cell_contents = props.unit_attribute.pre ? <div style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-all', hyphens: 'auto' }}>{cell_contents}</div> : cell_contents;
  return (
    cell_contents
  )
}

class Unit extends Component {
  constructor(props) {
    super(props);
    this.state = { show_details: false }
  }
  onExpand(event) {
    event.preventDefault();
    this.setState((state) => ({ show_details: !state.show_details }));
  }
  render() {
    let props = this.props;
    if (props.hide_ignored_units && props.ignored) { return null };
    const style = props.ignored ? { textDecoration: "line-through" } : {};
    let unit = props.metric_unit;
    if (unit.endsWith("s")) { unit = unit.substring(0, unit.length - 1) };
    return (
      <>
        <Table.Row key={props.unit.key} style={style}>
          <Table.Cell collapsing>
            <Icon size='large' name={this.state.show_details ? "caret down" : "caret right"} onClick={(e) => this.onExpand(e)}
              onKeyPress={(e) => this.onExpand(e)} tabIndex="0" />
          </Table.Cell>
          {props.unit_attributes.map((unit_attribute, col_index) =>
            <Table.Cell key={col_index}>
              <UnitAttribute unit={props.unit} unit_attribute={unit_attribute} />
            </Table.Cell>)
          }
          <Table.Cell collapsing>
          </Table.Cell>
        </Table.Row>
        {this.state.show_details && <Table.Row>
          <Table.Cell colSpan="99">
            <Grid stackable>
              <Grid.Row columns={2}>
                <Grid.Column width={4} verticalAlign='middle'>
                    <Radio
                      defaultChecked={props.ignored}
                      label={`Ignore this ${unit}`}
                      onChange={(e) => props.ignore_unit(e, props.source_uuid, props.unit.key)}
                      readOnly={props.readOnly}
                      toggle
                    />
                </Grid.Column>
                <Grid.Column width={12}>
                  <TextInput
                    label="Rationale"
                    readOnly={props.readOnly}
                    value=""
                  />
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Table.Cell>
        </Table.Row>}
      </>
    )
  }
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
    const unit_attributes = this.props.datamodel.sources[source_type].units[this.props.metric.type];
    const ignored_units = this.props.source.ignored_units || [];
    const metric_type = this.props.datamodel.metrics[this.props.metric.type];
    const metric_unit = this.props.metric.unit || metric_type.unit;
    const headers =
      <Table.Row>
        <Table.HeaderCell collapsing />
        {unit_attributes.map((unit_attribute) => <Table.HeaderCell key={unit_attribute.key}>{unit_attribute.name}</Table.HeaderCell>)}
        <Table.HeaderCell collapsing>
          <Popup trigger={
            <Button floated='right' icon primary size='small' basic disabled={ignored_units.length === 0}
              onClick={(e) => this.hide_ignored_units(e)}>
              <Icon name={this.state.hide_ignored_units ? 'unhide' : 'hide'} />
            </Button>} content={this.state.hide_ignored_units ? 'Show ignored items' : 'Hide ignored items'} />
        </Table.HeaderCell>
      </Table.Row>
    const rows = this.props.source.units.map((unit) =>
      <Unit key={unit.key} unit={unit} unit_attributes={unit_attributes} source_uuid={this.props.source.source_uuid}
        hide_ignored_units={this.state.hide_ignored_units} ignored={ignored_units.includes(unit.key)}
        readOnly={this.props.readOnly} ignore_unit={this.props.ignore_unit} metric_unit={metric_unit} />);
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

function SourcesUnits(props) {
  if (props.measurement == null) { return null };
  let panes = [];
  props.measurement.sources.forEach((source) => {
    const report_source = props.metric.sources[source.source_uuid];
    if (!report_source) { return }  // source was deleted, continue
    const source_type = report_source.type;
    const source_name = report_source.name || props.datamodel["sources"][source_type]["name"];
    let nr_units = source.value || 0;
    const nr_units_displayed = (source.units && source.units.length) || 0;
    if (Number(nr_units) !== Number(nr_units_displayed)) { nr_units = `${nr_units_displayed} of ${nr_units}` };
    panes.push({
      menuItem: (<Menu.Item key={source.source_uuid}>{source_name}<Label>{nr_units}</Label></Menu.Item>),
      render: () => <Tab.Pane>
        <SourceUnits source={source} datamodel={props.datamodel} metric={props.metric} readOnly={props.readOnly}
          ignore_unit={props.ignore_unit} report_uuid={props.report_uuid} metric_uuid={props.metric_uuid} />
      </Tab.Pane>
    })
  });
  return (
    <Tab panes={panes} />
  )
}

export { SourcesUnits };
