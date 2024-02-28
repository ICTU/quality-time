import { StatusIcon } from '../measurement/StatusIcon';
import { HyperLink } from '../widgets/HyperLink';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';

export function SourceEntityAttribute({ entity, entity_attribute }) {
    let cell_contents = entity[entity_attribute.key] ?? "";
    const type = entity_attribute.type ?? "";
    cell_contents = cell_contents && type === "datetime" ? <TimeAgoWithDate dateFirst date={cell_contents} /> : cell_contents;
    cell_contents = cell_contents && type === "date" ? <TimeAgoWithDate dateFirst noTime date={cell_contents} /> : cell_contents;
    cell_contents = cell_contents && type.includes("integer") ? Math.round(cell_contents).toString() : cell_contents;
    cell_contents = cell_contents && type.includes("percentage") ? cell_contents + "%" : cell_contents;
    cell_contents = cell_contents && type === "status" ? <StatusIcon status={cell_contents} /> : cell_contents;
    cell_contents = entity[entity_attribute.url] ? <HyperLink url={entity[entity_attribute.url]}>{cell_contents}</HyperLink> : cell_contents;
    cell_contents = entity_attribute.pre ? <pre data-testid="pre-wrapped" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{cell_contents}</pre> : <div style={{wordBreak: 'break-word'}}>{cell_contents}</div>;
    return (cell_contents);
}
