import React, { useContext } from 'react';
import { Message } from 'semantic-ui-react';
import { Segment } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { add_source, copy_source, move_source } from '../api/source';
import { AddButton, CopyButton, MoveButton } from '../widgets/Button';
import { source_options } from '../widgets/menu_options';
import { show_message } from '../widgets/toast';
import { pluralize } from '../utils';
import { Source } from './Source';
import { sourceTypeOptions } from './SourceType';

function ButtonSegment({ reports, metric_uuid, metric, reload }) {
    const dataModel = useContext(DataModel);
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <Segment vertical>
                <AddButton
                    item_type="source"
                    item_subtypes={sourceTypeOptions(dataModel, metric.type)}
                    onClick={(subtype) => add_source(metric_uuid, subtype, reload)}
                />
                <CopyButton
                    item_type="source"
                    onChange={(source_uuid) => copy_source(source_uuid, metric_uuid, reload)}
                    get_options={() => source_options(reports, dataModel, metric.type)}
                />
                <MoveButton
                    item_type="source"
                    onChange={(source_uuid) => move_source(source_uuid, metric_uuid, reload)}
                    get_options={() => source_options(reports, dataModel, metric.type, metric_uuid)}
                />
            </Segment>}
        />
    )
}

function SourceSegment({ report, metric, source_uuid, index, last_index, measurement_source, changed_fields, reload} ) {
    return (
        <Segment vertical>
            <Source
                first_source={index === 0}
                last_source={index === last_index}
                metric={metric}
                measurement_source={measurement_source}
                reload={reload}
                report={report}
                source_uuid={source_uuid}
                changed_fields={changed_fields}
            />
        </Segment>
    )
}

export function Sources({ reports, report, metric, metric_uuid, measurement, changed_fields, reload }) {
    const dataModel = useContext(DataModel)
    const measurementSources = measurement?.sources ?? [];
    const sourceUuids = Object.keys(metric.sources).filter((sourceUuid) =>
        dataModel.metrics[metric.type].sources.includes(metric.sources[sourceUuid].type)
    );

    const reload_source = (json) => {
        const nr_sources = json.nr_sources_mass_edited
        if (nr_sources > 0) {
            show_message("info", `Changed ${nr_sources} ${pluralize("source", nr_sources)}`)
        }
        reload(json)
    }

    const lastIndex = sourceUuids.length - 1;
    const sourceSegments = sourceUuids.map((sourceUuid, index) => {
        return (
            <SourceSegment
                key={sourceUuid}
                report={report}
                metric={metric}
                source_uuid={sourceUuid}
                index={index}
                last_index={lastIndex}
                measurement_source={measurementSources.find((source) => source.source_uuid === sourceUuid)}
                changed_fields={changed_fields}
                reload={reload_source}
            />
        )
    });
    return (
        <>
            {sourceSegments.length === 0 ? <Message><Message.Header>No sources</Message.Header><p>No sources have been configured yet.</p></Message> : sourceSegments}
            <ButtonSegment reports={reports} metric_uuid={metric_uuid} metric={metric} reload={reload} />
        </>
    )
}
