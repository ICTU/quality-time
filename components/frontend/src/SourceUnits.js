import React, { Component } from 'react';
import { Button, Grid, Icon, Table, Popup, Radio } from 'semantic-ui-react';
import { TextInput } from './fields/TextInput';
import { TableRowWithDetails } from './TableRowWithDetails';

function UnitAttribute(props) {
  let cell_contents = props.unit[props.unit_attribute.key];
  cell_contents = props.unit[props.unit_attribute.url] ? <a href={props.unit[props.unit_attribute.url]}>{cell_contents}</a> : cell_contents;
  cell_contents = props.unit_attribute.pre ? <div style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-all', hyphens: 'auto' }}>{cell_contents}</div> : cell_contents;
  return (
    cell_contents
  )
}

function UnitDetails(props) {
  return (
    <Grid stackable>
      <Grid.Row columns={2}>
        <Grid.Column width={4} verticalAlign='middle'>
          <Radio
            defaultChecked={props.ignored}
            label={`Ignore this ${props.unit_name}`}
            onChange={(e) => props.ignore_unit(e, props.source_uuid, props.unit.key)}
            readOnly={props.readOnly}
            toggle
          />
        </Grid.Column>
        <Grid.Column width={12}>
          <TextInput
            label="Rationale"
            placeholder={`Rationale for ignoring this ${props.unit_name}...`}
            readOnly={props.readOnly}
            value={props.rationale_for_ignoring_unit}
            set_value={(value) => props.set_rationale_for_ignoring_unit(props.source_uuid, props.unit.key, value)}
          />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  )
}

class Unit extends Component {
  render() {
    let props = this.props;
    if (props.hide_ignored_units && props.ignored) { return null };
    const style = props.ignored ? { textDecoration: "line-through" } : {};
    let unit_name = props.metric_unit;
    if (unit_name.endsWith("s")) { unit_name = unit_name.substring(0, unit_name.length - 1) };
    var negative, warning;
    props.unit_attributes.forEach((unit_attribute) => {
      let cell_contents = props.unit[unit_attribute.key];
      if (unit_attribute.color && unit_attribute.color[cell_contents]) {
        negative = (unit_attribute.color[cell_contents] === "negative");
        warning = (unit_attribute.color[cell_contents] === "warning");
        return;
      }
    })
    const details = <UnitDetails
      ignored={props.ignored}
      ignore_unit={props.ignore_unit}
      rationale_for_ignoring_unit={props.rationale_for_ignoring_unit}
      readOnly={props.readOnly}
      set_rationale_for_ignoring_unit={props.ignored_units_rationale}
      source_uuid={props.source_uuid}
      unit={props.unit}
      unit_name={unit_name}
    />
    return (
      <TableRowWithDetails key={props.unit.key} style={style} details={details} negative={negative} warning={warning}>
        {props.unit_attributes.map((unit_attribute, col_index) =>
          <Table.Cell key={col_index}>
            <UnitAttribute unit={props.unit} unit_attribute={unit_attribute} />
          </Table.Cell>)
        }
        <Table.Cell collapsing />
      </TableRowWithDetails>
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
      <Unit
        hide_ignored_units={this.state.hide_ignored_units}
        ignore_unit={this.props.ignore_unit}
        ignored={ignored_units.includes(unit.key)}
        key={unit.key}
        metric_unit={metric_unit}
        rationale_for_ignoring_unit={this.props.source.ignored_units_rationale ? this.props.source.ignored_units_rationale[unit.key] : ""}
        readOnly={this.props.readOnly}
        set_rationale_for_ignoring_unit={this.props.set_rationale_for_ignoring_unit}
        source_uuid={this.props.source.source_uuid}
        unit={unit}
        unit_attributes={unit_attributes}
      />);
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

export { SourceUnits };
