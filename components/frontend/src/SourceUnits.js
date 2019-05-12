import React, { Component } from 'react';
import { Button, Grid, Header, Icon, Popup, Table } from 'semantic-ui-react';
import { TextInput } from './fields/TextInput';
import { SingleChoiceInput } from './fields/SingleChoiceInput';
import { TableRowWithDetails } from './TableRowWithDetails';

function UnitAttribute(props) {
  let cell_contents = props.unit[props.unit_attribute.key];
  cell_contents = cell_contents && props.unit_attribute.type === "datetime" ? new Date(cell_contents).toLocaleString() : cell_contents;
  cell_contents = cell_contents && props.unit_attribute.type === "date" ? new Date(cell_contents).toLocaleDateString() : cell_contents;
  cell_contents = props.unit[props.unit_attribute.url] ? <a href={props.unit[props.unit_attribute.url]}>{cell_contents}</a> : cell_contents;
  cell_contents = props.unit_attribute.pre ? <div style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-all', hyphens: 'auto' }}>{cell_contents}</div> : cell_contents;
  return (
    cell_contents
  )
}

function UnitDetails(props) {
  const options = [
    {key: 'unconfirmed', text: 'Unconfirmed', value: 'unconfirmed',
     content: <Header as="h5" content="Unconfirmed" subheader={`This ${props.unit_name} should be reviewed to decide what to do with it`} />},
    {key: 'confirmed', text: 'Confirmed', value: 'confirmed',
     content: <Header as="h5" content="Confirmed" subheader={`This ${props.unit_name} has been reviewed and should be dealt with`} />},
    {key: 'false_positive', text: 'False positive', value: 'false_positive',
     content: <Header as="h5" content="False positive" subheader={`This ${props.unit_name} can be ignored because it's been incorrectly identified as ${props.unit_name}`} />},
    {key: 'fixed', text: 'Fixed', value: 'fixed',
     content: <Header as="h5" content="Fixed" subheader={`This ${props.unit_name} has been fixed and will disappear shortly`} />},
    {key: 'wont_fix', text: "Won't fix", value: "wont_fix",
     content: <Header as="h5" content="Won't fix" subheader={`This ${props.unit_name} will not be fixed`} />}
  ];
  return (
    <Grid stackable>
      <Grid.Row columns={4}>
        <Grid.Column width={4}>
          <SingleChoiceInput
            label={`${props.unit_name[0].toUpperCase()}${props.unit_name.slice(1)} status`}
            options={options}
            readOnly={props.readOnly}
            set_value={(value) => props.set_unit_attribute(props.source_uuid, props.unit.key, "status", value)}
            value={props.status}
          />
        </Grid.Column>
        <Grid.Column width={12}>
          <TextInput
            label="Rationale"
            placeholder={`Rationale for ${props.unit_name} status...`}
            readOnly={props.readOnly}
            set_value={(value) => props.set_unit_attribute(props.source_uuid, props.unit.key, "rationale", value)}
            value={props.rationale}
          />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  )
}

class Unit extends Component {
  render() {
    let props = this.props;
    const ignored_unit = ["wont_fix", "fixed", "false_positive"].indexOf(props.status) > -1;
    if (props.hide_ignored_units && ignored_unit ) { return null };
    const style = ignored_unit ? { textDecoration: "line-through" } : {};
    let unit_name = props.metric_unit;
    if (unit_name.endsWith("s")) { unit_name = unit_name.substring(0, unit_name.length - 1) };
    var positive, negative, warning, active;
    props.unit_attributes.forEach((unit_attribute) => {
      let cell_contents = props.unit[unit_attribute.key];
      if (unit_attribute.color && unit_attribute.color[cell_contents]) {
        positive = (unit_attribute.color[cell_contents] === "positive");
        negative = (unit_attribute.color[cell_contents] === "negative");
        warning = (unit_attribute.color[cell_contents] === "warning");
        active = (unit_attribute.color[cell_contents] === "active");
        return;
      }
    })
    const details = <UnitDetails
      status={props.status}
      rationale={props.rationale}
      readOnly={props.readOnly}
      set_unit_attribute={props.set_unit_attribute}
      source_uuid={props.source_uuid}
      unit={props.unit}
      unit_name={unit_name}
    />
    return (
      <TableRowWithDetails key={props.unit.key} style={style} details={details}
        active={active} positive={positive} negative={negative} warning={warning}>
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
    const metric_type = this.props.datamodel.metrics[this.props.metric.type];
    const metric_unit = this.props.metric.unit || metric_type.unit;
    const headers =
      <Table.Row>
        <Table.HeaderCell collapsing />
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
      <Unit
        hide_ignored_units={this.state.hide_ignored_units}
        status={
          this.props.source.unit_user_data && this.props.source.unit_user_data[unit.key] &&
          this.props.source.unit_user_data[unit.key].status ? this.props.source.unit_user_data[unit.key].status : "unconfirmed"}
        key={unit.key}
        metric_unit={metric_unit}
        rationale={
          this.props.source.unit_user_data && this.props.source.unit_user_data[unit.key] &&
          this.props.source.unit_user_data[unit.key].rationale ? this.props.source.unit_user_data[unit.key].rationale : ""}
        readOnly={this.props.readOnly}
        set_unit_attribute={this.props.set_unit_attribute}
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
