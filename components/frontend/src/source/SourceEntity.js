import { useState } from 'react';
import { bool, func, string } from 'prop-types';
import { Table } from 'semantic-ui-react';
import { IssueStatus } from '../issue/IssueStatus';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { SourceEntityDetails } from './SourceEntityDetails';
import { SourceEntityAttribute } from './SourceEntityAttribute';
import { source_entity_status_name } from './source_entity_status';
import { alignment } from './SourceEntities';
import { entityAttributesPropType, entityPropType, entityStatusPropType, metricPropType, reportPropType, settingsPropType } from '../sharedPropTypes';
import "./SourceEntity.css";

function entityCanBeIgnored(status, statusEndDateString) {
    const statusEndDate = new Date(statusEndDateString);
    const now = new Date();
    if (statusEndDate < now) { return false }
    return ["wont_fix", "fixed", "false_positive"].includes(status);
}
entityCanBeIgnored.propTypes = {
    status: entityStatusPropType,
    statusEndDateString: string
}

export function SourceEntity(
    {
        metric,
        metric_uuid,
        source_uuid,
        hide_ignored_entities,
        entity,
        entity_name,
        entity_attributes,
        rationale,
        reload,
        report,
        settings,
        status,
        status_end_date
    }
) {
    const [expanded, setExpanded] = useState(false);

    const ignoredEntity = entityCanBeIgnored(status, status_end_date)
    if (hide_ignored_entities && ignoredEntity) {
        return null;
    }
    const style = ignoredEntity ? { textDecoration: "line-through" } : {};
    let statusClassName = "unknown_status";
    for (let entity_attribute of entity_attributes) {
        let cell_contents = entity[entity_attribute.key];
        if (entity_attribute.color?.[cell_contents]) {
            statusClassName = entity_attribute.color[cell_contents] + '_status';
            break
        }
    }
    const details = <SourceEntityDetails
        entity={entity}
        metric={metric}
        metric_uuid={metric_uuid}
        name={entity_name}
        rationale={rationale}
        reload={reload}
        report={report}
        source_uuid={source_uuid}
        status={status}
        status_end_date={status_end_date}
    />;
    return (
        <TableRowWithDetails className={statusClassName} details={details} key={entity.key} expanded={expanded} onExpand={setExpanded}>
            <Table.Cell style={style}>{source_entity_status_name[status]}</Table.Cell>
            <Table.Cell style={style}>{status === "unconfirmed" ? "" : status_end_date}</Table.Cell>
            <Table.Cell style={style}>{status === "unconfirmed" ? "" : rationale}</Table.Cell>
            <Table.Cell style={style}>{entity.first_seen ? <TimeAgoWithDate dateFirst date={entity.first_seen} /> : ""}</Table.Cell>
            <Table.Cell>
                <IssueStatus entityKey={entity.key} metric={metric} issueTrackerMissing={!report.issue_tracker} settings={settings} />
            </Table.Cell>
            {entity_attributes.map((entity_attribute) =>
                <Table.Cell
                    key={entity_attribute.key}
                    style={style}
                    textAlign={alignment(entity_attribute.type, entity_attribute.alignment)}
                >
                    <SourceEntityAttribute entity={entity} entity_attribute={entity_attribute} />
                </Table.Cell>)}
        </TableRowWithDetails>
    );
}
SourceEntity.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    source_uuid: string,
    hide_ignored_entities: bool,
    entity: entityPropType,
    entity_name: string,
    entity_attributes: entityAttributesPropType,
    rationale: string,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    status: entityStatusPropType,
    status_end_date: string,
}
