import React from 'react';
import { Segment } from 'semantic-ui-react';
import { Source } from './Source';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { AddButton, CopyButton, MoveButton } from '../widgets/Button';
import { add_source, copy_source, move_source } from '../api/source';
import { source_options } from '../widgets/menu_options';

export function Sources({ datamodel, reports, report, metric_uuid, metric_type, metric_unit, sources, measurement, changed_fields, reload }) {
    const measurement_sources = measurement ? measurement.sources : [];
    function source_error(source_uuid, error_type) {
        return measurement_sources.find((source) => source.source_uuid === source_uuid)?.[error_type] || '';
    }
    function ButtonSegment() {
        return (
            <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                <Segment vertical>
                    <AddButton item_type="source" onClick={() => add_source(metric_uuid, reload)} />
                    <CopyButton
                        item_type="source"
                        onChange={(source_uuid) => copy_source(source_uuid, metric_uuid, reload)}
                        get_options={() => source_options(reports, datamodel, metric_type)}
                    />
                    <MoveButton
                        item_type="source"
                        onChange={(source_uuid) => move_source(source_uuid, metric_uuid, reload)}
                        get_options={() => source_options(reports, datamodel, metric_type, metric_uuid)}
                    />
                </Segment>}
            />
        )
    }
    const source_uuids = Object.keys(sources).filter((source_uuid) =>
        datamodel.metrics[metric_type].sources.includes(sources[source_uuid].type)
    );
    const last_index = source_uuids.length - 1;

    function SourceSegment(source_uuid, index) {
        return (
            <Segment vertical key={source_uuid}>
                <Source
                    connection_error={source_error(source_uuid, "connection_error")}
                    datamodel={datamodel}
                    first_source={index === 0}
                    last_source={index === last_index}
                    metric_type={metric_type}
                    metric_uuid={metric_uuid}
                    metric_unit={metric_unit}
                    parse_error={source_error(source_uuid, "parse_error")}
                    reload={reload}
                    report={report}
                    reports={reports}
                    source={sources[source_uuid]}
                    source_uuid={source_uuid}
                    changed_fields={changed_fields}
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
