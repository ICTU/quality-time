import React from 'react';
import { Table, TableRow } from 'semantic-ui-react';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { SourceEntityDetails } from './SourceEntityDetails';
import { SourceEntityAttribute } from './SourceEntityAttribute';
import { source_entity_status_name } from './source_entity_status';
import { alignment } from './SourceEntities';
import "./SourceEntity.css";
import { EDIT_ENTITY_PERMISSION, ReadOnlyOrEditable } from '../context/ReadOnly';

export function SourceEntity(props) {
  const ignored_entity = ["wont_fix", "fixed", "false_positive"].includes(props.status);
  if (props.hide_ignored_entities && ignored_entity) {
    return null;
  }
  const style = ignored_entity ? { textDecoration: "line-through" } : {};
  var status = "unknown_status";
  props.entity_attributes.forEach((entity_attribute) => {
    let cell_contents = props.entity[entity_attribute.key];
    if (entity_attribute.color && entity_attribute.color[cell_contents]) {
      status = entity_attribute.color[cell_contents] + '_status';
      return;
    }
  });
  const details = <SourceEntityDetails
    entity={props.entity}
    metric_uuid={props.metric_uuid}
    name={props.entity_name}
    rationale={props.rationale}
    reload={props.reload}
    source_uuid={props.source_uuid}
    status={props.status}
  />;
  const entityCells = <>
    <Table.Cell>{source_entity_status_name[props.status]}</Table.Cell>
    {props.entity_attributes.map((entity_attribute, col_index) =>
      <Table.Cell key={col_index} textAlign={alignment(entity_attribute.type)}>
        <SourceEntityAttribute entity={props.entity} entity_attribute={entity_attribute} />
      </Table.Cell>)}
  </>;
  return (
    <TableRowWithDetails className={status} details={details} key={props.entity.key} style={style}>
      {entityCells}
    </TableRowWithDetails>
  );
}
