import React, { Component } from 'react';
import { Button, Popup, Table } from 'semantic-ui-react';
import { SourceEntity } from './SourceEntity';

class SourceEntities extends Component {
  constructor(props) {
    super(props);
    this.state = { hide_ignored_entities: false, sort_column: null, sort_direction: null };
  }

  hide_ignored_entities(event) {
    event.preventDefault();
    this.setState({ hide_ignored_entities: !this.state.hide_ignored_entities })
  }

  handle_sort(event, column) {
    event.preventDefault();
    const sort_direction = this.state.sort_direction;
    this.setState(
      {
        sort_column: column,
        sort_direction: sort_direction === 'ascending' ? 'descending' : 'ascending'
      })
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
    const { hide_ignored_entities, sort_column, sort_direction } = this.state;
    const headers =
      <Table.Row>
        <Table.HeaderCell collapsing textAlign="center">
          <Popup trigger={
            <Button
              basic
              compact
              icon={hide_ignored_entities ? 'unhide' : 'hide'}
              onClick={(e) => this.hide_ignored_entities(e)}
              primary
            />
          } content={hide_ignored_entities ? `Show resolved ${entity_name_plural}` : `Hide resolved ${entity_name_plural}`} />
        </Table.HeaderCell>
        {entity_attributes.map((entity_attribute) =>
          <Table.HeaderCell
            key={entity_attribute.key}
            sorted={sort_column === entity_attribute.key ? sort_direction : null}
            onClick={(event) => this.handle_sort(event, entity_attribute.key)}
          >
            {entity_attribute.name}
          </Table.HeaderCell>)
        }
      </Table.Row>
    const rows = this.props.source.entities.map((entity) =>
      <SourceEntity
        entity={entity}
        entity_attributes={entity_attributes}
        entity_name={entity_name}
        hide_ignored_entities={hide_ignored_entities}
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
      <Table sortable size='small'>
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
