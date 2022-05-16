import React, { useState } from 'react';
import { Table } from 'semantic-ui-react';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { SourceEntityDetails } from './SourceEntityDetails';
import { SourceEntityAttribute } from './SourceEntityAttribute';
import { source_entity_status_name } from './source_entity_status';
import { alignment } from './SourceEntities';
import "./SourceEntity.css";

function entityCanBeIgnored(status, status_end_date) {
    const statusEndDate = new Date(status_end_date);
    const now = new Date();
    if (statusEndDate < now) { return false}
    return ["wont_fix", "fixed", "false_positive"].includes(status);
}

export function SourceEntity({ metric_uuid, source_uuid, hide_ignored_entities, entity, entity_name, entity_attributes, rationale, reload, status, status_end_date }) {
    const [expanded, setExpanded] = useState(false);

    const ignoredEntity = entityCanBeIgnored(status, status_end_date)
    if (hide_ignored_entities && ignoredEntity) {
        return null;
    }
    const style = ignoredEntity ? { textDecoration: "line-through" } : {};
    var statusClassName = "unknown_status";
    for (let entity_attribute of entity_attributes) {
        let cell_contents = entity[entity_attribute.key];
        if (entity_attribute.color && entity_attribute.color[cell_contents]) {
            statusClassName = entity_attribute.color[cell_contents] + '_status';
            break
        }
    }
    const details = <SourceEntityDetails
        entity={entity}
        metric_uuid={metric_uuid}
        name={entity_name}
        rationale={rationale}
        reload={reload}
        source_uuid={source_uuid}
        status={status}
        status_end_date={status_end_date}
    />;
    const entityCells = <>
        <Table.Cell style={style}>{source_entity_status_name[status]}</Table.Cell>
        <Table.Cell style={style}>{status === "unconfirmed" ? "" : status_end_date}</Table.Cell>
        <Table.Cell style={style}>{status === "unconfirmed" ? "" : rationale}</Table.Cell>
        {entity_attributes.map((entity_attribute, col_index) =>
            <Table.Cell
                key={col_index}
                style={style}
                textAlign={alignment(entity_attribute.type, entity_attribute.alignment)}
            >
                <SourceEntityAttribute entity={entity} entity_attribute={entity_attribute} />
            </Table.Cell>)}
    </>;
    return (
        <TableRowWithDetails className={statusClassName} details={details} key={entity.key} expanded={expanded} onExpand={setExpanded}>
            {entityCells}
        </TableRowWithDetails>
    );
}
