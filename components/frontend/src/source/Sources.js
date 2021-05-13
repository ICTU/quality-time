import React from 'react';
import { Segment } from 'semantic-ui-react';
import { Source } from './Source';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/ReadOnly';
import { AddButton, CopyButton, MoveButton } from '../widgets/Button';
import { add_source, copy_source, move_source } from '../api/source';
import { source_options } from '../widgets/menu_options';

export function Sources(props) {
    const measurement_sources = props.measurement ? props.measurement.sources : [];
    function source_error(source_uuid, error_type) {
        return measurement_sources.find((source) => source.source_uuid === source_uuid)?.[error_type] || '';
    }
    function ButtonSegment() {
        return (
            <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                <Segment vertical>
                    <AddButton item_type="source" onClick={() => add_source(props.metric_uuid, props.reload)} />
                    <CopyButton
                        item_type="source"
                        onChange={(source_uuid) => copy_source(source_uuid, props.metric_uuid, props.reload)}
                        get_options={() => source_options(props.reports, props.datamodel, props.metric_type)}
                    />
                    <MoveButton
                        item_type="source"
                        onChange={(source_uuid) => move_source(source_uuid, props.metric_uuid, props.reload)}
                        get_options={() => source_options(props.reports, props.datamodel, props.metric_type, props.metric_uuid)}
                    />
                </Segment>}
            />
        )
    }
    const source_uuids = Object.keys(props.sources).filter((source_uuid) =>
        props.datamodel.metrics[props.metric_type].sources.includes(props.sources[source_uuid].type)
    );
    const last_index = source_uuids.length - 1;

    function SourceSegment(source_uuid, index) {
        return (
            <Segment vertical key={source_uuid}>
                <Source
                    connection_error={source_error(source_uuid, "connection_error")}
                    datamodel={props.datamodel}
                    first_source={index === 0}
                    last_source={index === last_index}
                    metric_type={props.metric_type}
                    metric_uuid={props.metric_uuid}
                    metric_unit={props.metric_unit}
                    parse_error={source_error(source_uuid, "parse_error")}
                    reload={props.reload}
                    report={props.report}
                    reports={props.reports}
                    source={props.sources[source_uuid]}
                    source_uuid={source_uuid}
                    changed_fields={props.changed_fields}
                />
            </Segment>
        )
    }
    return (
        <>
            {source_uuids.map((source_uuid, index) => SourceSegment(source_uuid, index))}
            <ButtonSegment />
        </>
    )
}
