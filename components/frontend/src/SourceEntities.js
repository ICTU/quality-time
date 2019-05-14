import React, { Component } from 'react';
import { Button, Grid, Header, Icon, Popup, Table } from 'semantic-ui-react';
import { TextInput } from './fields/TextInput';
import { SingleChoiceInput } from './fields/SingleChoiceInput';
import { TableRowWithDetails } from './TableRowWithDetails';

function EntityAttribute(props) {
  let cell_contents = props.entity[props.entity_attribute.key];
  cell_contents = cell_contents && props.entity_attribute.type === "datetime" ? new Date(cell_contents).toLocaleString() : cell_contents;
  cell_contents = cell_contents && props.entity_attribute.type === "date" ? new Date(cell_contents).toLocaleDateString() : cell_contents;
  cell_contents = props.entity[props.entity_attribute.url] ? <a href={props.entity[props.entity_attribute.url]}>{cell_contents}</a> : cell_contents;
  cell_contents = props.entity_attribute.pre ? <div style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-all', hyphens: 'auto' }}>{cell_contents}</div> : cell_contents;
  return (
    cell_contents
  )
}

function EntityDetails(props) {
  const options = [
    {key: 'unconfirmed', text: 'Unconfirmed', value: 'unconfirmed',
     content: <Header as="h5" content="Unconfirm" subheader={`This ${props.name} should be reviewed to decide what to do with it.`} />},
    {key: 'confirmed', text: 'Confirmed', value: 'confirmed',
     content: <Header as="h5" content="Confirm" subheader={`This ${props.name} has been reviewed and should be dealt with.`} />},
    {key: 'fixed', text: 'Fixed', value: 'fixed',
     content: <Header as="h5" content="Resolve as fixed" subheader={`This ${props.name} has been fixed and will disappear shortly.`} />},
    {key: 'false_positive', text: 'False positive', value: 'false_positive',
     content: <Header as="h5" content="Resolve as false positive" subheader={`This ${props.name} can be ignored because it's been incorrectly identified as ${props.name}.`} />},
    {key: 'wont_fix', text: "Won't fix", value: "wont_fix",
     content: <Header as="h5" content="Resolve as won't fix" subheader={`This ${props.name} will not be fixed.`} />}
  ];
  return (
    <Grid stackable>
      <Grid.Row columns={4}>
        <Grid.Column width={4}>
          <SingleChoiceInput
            label={`${props.name[0].toUpperCase()}${props.name.slice(1)} status`}
            options={options}
            readOnly={props.readOnly}
            set_value={(value) => props.set_entity_attribute(props.source_uuid, props.entity.key, "status", value)}
            value={props.status}
          />
        </Grid.Column>
        <Grid.Column width={12}>
          <TextInput
            label="Rationale"
            placeholder={`Rationale for ${props.name} status...`}
            readOnly={props.readOnly}
            set_value={(value) => props.set_entity_attribute(props.source_uuid, props.entity.key, "rationale", value)}
            value={props.rationale}
          />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  )
}

class Entity extends Component {
  render() {
    let props = this.props;
    const ignored_entity = ["wont_fix", "fixed", "false_positive"].indexOf(props.status) > -1;
    if (props.hide_ignored_entities && ignored_entity ) { return null };
    const style = ignored_entity ? { textDecoration: "line-through" } : {};
    var positive, negative, warning, active;
    props.entity_attributes.forEach((entity_attribute) => {
      let cell_contents = props.entity[entity_attribute.key];
      if (entity_attribute.color && entity_attribute.color[cell_contents]) {
        positive = (entity_attribute.color[cell_contents] === "positive");
        negative = (entity_attribute.color[cell_contents] === "negative");
        warning = (entity_attribute.color[cell_contents] === "warning");
        active = (entity_attribute.color[cell_contents] === "active");
        return;
      }
    })
    const details = <EntityDetails
      name={props.entity_name}
      status={props.status}
      rationale={props.rationale}
      readOnly={props.readOnly}
      set_entity_attribute={props.set_entity_attribute}
      source_uuid={props.source_uuid}
      entity={props.entity}
    />
    return (
      <TableRowWithDetails key={props.entity.key} style={style} details={details}
        active={active} positive={positive} negative={negative} warning={warning}>
        {props.entity_attributes.map((entity_attribute, col_index) =>
          <Table.Cell key={col_index}>
            <EntityAttribute entity={props.entity} entity_attribute={entity_attribute} />
          </Table.Cell>)
        }
        <Table.Cell collapsing />
      </TableRowWithDetails>
    )
  }
}

class SourceEntities extends Component {
  constructor(props) {
    super(props);
    this.state = { hide_ignored_entities: false };
  }

  hide_ignored_entities(event) {
    event.preventDefault();
    this.setState({ hide_ignored_entities: !this.state.hide_ignored_entities })
  }

  render() {
    if (!Array.isArray(this.props.source.entities) || this.props.source.entities.length === 0) {
      return null;
    }
    const report_source = this.props.metric.sources[this.props.source.source_uuid];
    const source_type = report_source.type;
    const entity_attributes = this.props.datamodel.sources[source_type].entities[this.props.metric.type].attributes;
    const entity_name = this.props.datamodel.sources[source_type].entities[this.props.metric.type].name;
    const entity_name_plural = this.props.datamodel.sources[source_type].entities[this.props.metric.type].name_plural;
    const headers =
      <Table.Row>
        <Table.HeaderCell collapsing />
        {entity_attributes.map((entity_attribute) => <Table.HeaderCell key={entity_attribute.key}>{entity_attribute.name}</Table.HeaderCell>)}
        <Table.HeaderCell collapsing>
          <Popup trigger={
            <Button floated='right' icon primary size='small' basic
              onClick={(e) => this.hide_ignored_entities(e)}>
              <Icon name={this.state.hide_ignored_entities ? 'unhide' : 'hide'} />
            </Button>} content={this.state.hide_ignored_entities ? `Show resolved ${entity_name_plural}` : `Hide resolved ${entity_name_plural}`} />
        </Table.HeaderCell>
      </Table.Row>
    const rows = this.props.source.entities.map((entity) =>
      <Entity
        entity={entity}
        entity_attributes={entity_attributes}
        entity_name={entity_name}
        hide_ignored_entities={this.state.hide_ignored_entities}
        key={entity.key}
        status={
          this.props.source.entity_user_data && this.props.source.entity_user_data[entity.key] &&
          this.props.source.entity_user_data[entity.key].status ? this.props.source.entity_user_data[entity.key].status : "unconfirmed"}
        rationale={
          this.props.source.entity_user_data && this.props.source.entity_user_data[entity.key] &&
          this.props.source.entity_user_data[entity.key].rationale ? this.props.source.entity_user_data[entity.key].rationale : ""}
        readOnly={this.props.readOnly}
        set_entity_attribute={this.props.set_entity_attribute}
        source_uuid={this.props.source.source_uuid}
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

export { SourceEntities };
