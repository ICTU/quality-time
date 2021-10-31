import React from 'react';
import { StatusIcon } from '../metric/StatusIcon';
import { HyperLink } from '../widgets/HyperLink';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { format_minutes } from '../utils';

export function SourceEntityAttribute({ entity, entity_attribute }) {
    let cell_contents = entity[entity_attribute.key] || "";
    cell_contents = cell_contents && entity_attribute.type === "datetime" ? <TimeAgoWithDate dateFirst date={cell_contents} /> : cell_contents;
    cell_contents = cell_contents && entity_attribute.type === "date" ? <TimeAgoWithDate dateFirst noTime date={cell_contents} /> : cell_contents;
    cell_contents = cell_contents && entity_attribute.type === "minutes" ? format_minutes(cell_contents) : cell_contents;
    cell_contents = cell_contents && entity_attribute.type === "status" ? <StatusIcon status={cell_contents} /> : cell_contents;
    cell_contents = entity[entity_attribute.url] ? <HyperLink url={entity[entity_attribute.url]}>{cell_contents}</HyperLink> : cell_contents;
    cell_contents = entity_attribute.pre ? <pre data-testid="pre-wrapped" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{cell_contents}</pre> : cell_contents;
    return (cell_contents);
}
