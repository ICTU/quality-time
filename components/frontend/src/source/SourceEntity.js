import React from 'react';
import { Table } from 'semantic-ui-react';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { SourceEntityDetails } from './SourceEntityDetails';
import { SourceEntityAttribute } from './SourceEntityAttribute';
import "./SourceEntity.css";

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
  return (
    <TableRowWithDetails className={status} details={details} key={props.entity.key} style={style}>
      {props.entity_attributes.map((entity_attribute, col_index) =>
        <Table.Cell key={col_index}>
          <SourceEntityAttribute entity={props.entity} entity_attribute={entity_attribute} />
        </Table.Cell>)}
    </TableRowWithDetails>
  );
}
