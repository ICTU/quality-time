import React, { useState } from 'react';
import { Button, Popup, Table } from 'semantic-ui-react';
import { SourceEntity } from './SourceEntity';

export function SourceEntities(props) {
  const [hideIgnoredEntities, setHideIgnoredEntities] = useState(false);
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('ascending');

  const report_source = props.metric.sources[props.source.source_uuid];
  const source_type = report_source.type;
  const metric_entities = props.datamodel.sources[source_type].entities[props.metric.type];
  if (!metric_entities || !Array.isArray(props.source.entities) || props.source.entities.length === 0) {
    return null;
  }
  const entity_attributes = metric_entities.attributes;
  const entity_name = metric_entities.name;
  const entity_name_plural = metric_entities.name_plural;
  const headers =
    <Table.Row>
      <Table.HeaderCell collapsing textAlign="center">
        <Popup trigger={
          <Button
            basic
            compact
            icon={hideIgnoredEntities ? 'unhide' : 'hide'}
            onClick={() => setHideIgnoredEntities(!hideIgnoredEntities)}
            primary
          />
        } content={hideIgnoredEntities ? `Show resolved ${entity_name_plural}` : `Hide resolved ${entity_name_plural}`} />
      </Table.HeaderCell>
      {entity_attributes.map((entity_attribute) =>
        <Table.HeaderCell
          key={entity_attribute.key}
          sorted={sortColumn === entity_attribute.key ? sortDirection : null}
          onClick={() => {
            if (entity_attribute.key === sortColumn) {
              setSortDirection(sortDirection === 'ascending' ? 'descending' : 'ascending')
            } else {
              setSortColumn(entity_attribute.key)
            }
          }}
        >
          {entity_attribute.name}
        </Table.HeaderCell>)
      }
    </Table.Row>
  let entities = Array.from(props.source.entities);
  if (sortColumn !== null) {
    entities.sort((a, b) => a[sortColumn] < b[sortColumn] ? -1 : 1)
    if (sortDirection === 'descending') {
      entities.reverse()
    }
  }
  const rows = entities.map((entity) =>
    <SourceEntity
      entity={entity}
      entity_attributes={entity_attributes}
      entity_name={entity_name}
      fetch_measurement_and_reload={props.fetch_measurement_and_reload}
      hide_ignored_entities={hideIgnoredEntities}
      key={entity.key}
      metric_uuid={props.metric_uuid}
      status={
        props.source.entity_user_data && props.source.entity_user_data[entity.key] &&
          props.source.entity_user_data[entity.key].status ? props.source.entity_user_data[entity.key].status : "unconfirmed"}
      rationale={
        props.source.entity_user_data && props.source.entity_user_data[entity.key] &&
          props.source.entity_user_data[entity.key].rationale ? props.source.entity_user_data[entity.key].rationale : ""}
      readOnly={props.readOnly}
      source_uuid={props.source.source_uuid}
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
