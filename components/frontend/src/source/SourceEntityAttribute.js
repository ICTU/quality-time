import React from 'react';
import { StatusIcon } from '../measurement/StatusIcon';
import { HyperLink } from '../widgets/HyperLink';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';

export function SourceEntityAttribute({ entity, entity_attribute }) {
    let cell_contents = entity[entity_attribute.key] ?? "";
    cell_contents = cell_contents && entity_attribute.type === "datetime" ? <TimeAgoWithDate dateFirst date={cell_contents} /> : cell_contents;
    cell_contents = cell_contents && entity_attribute.type === "date" ? <TimeAgoWithDate dateFirst noTime date={cell_contents} /> : cell_contents;
    cell_contents = cell_contents && entity_attribute.type === "integer" ? Math.round(cell_contents) : cell_contents;
    cell_contents = cell_contents && entity_attribute.type === "status" ? <StatusIcon status={cell_contents} /> : cell_contents;
    cell_contents = entity[entity_attribute.url] ? <HyperLink url={entity[entity_attribute.url]}>{cell_contents}</HyperLink> : cell_contents;
    cell_contents = entity_attribute.pre ? <pre data-testid="pre-wrapped" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{cell_contents}</pre> : <div style={{wordBreak: 'break-word'}}>{cell_contents}</div>;
    return (cell_contents);
}
