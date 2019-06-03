import React from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
import { Source } from './Source';
import { add_source } from '../api/source';

export function Sources(props) {
    function source_error(measurement_sources, source_uuid, error_type) {
        let message = '';
        measurement_sources.forEach((source) => {
            if (source.source_uuid === source_uuid) {
                message = source[error_type] || '';
                return
            }
        });
        return message;
    }
    const source_uuids = Object.keys(props.sources).filter((source_uuid) =>
        props.datamodel.metrics[props.metric_type].sources.includes(props.sources[source_uuid].type)
    );
    const measurement_sources = props.measurement ? props.measurement.sources : [];
    const sources = source_uuids.map((source_uuid) =>
        (
            <Segment vertical key={source_uuid}>
                <Source
                    connection_error={source_error(measurement_sources, source_uuid, "connection_error")}
                    datamodel={props.datamodel}
                    metric_type={props.metric_type}
                    parse_error={source_error(measurement_sources, source_uuid, "parse_error")}
                    readOnly={props.readOnly}
                    reload={props.reload}
                    report={props.report}
                    source={props.sources[source_uuid]}
                    source_uuid={source_uuid}
                />
            </Segment>
        )
    );
    return (
        <>
            {sources}
            {!props.readOnly && <Segment vertical>
                <Button
                    basic
                    icon
                    onClick={() => add_source(props.report.report_uuid, props.metric_uuid, props.reload)}
                    primary
                >
                    <Icon name='plus' /> Add source
                </Button>
            </Segment>}
        </>
    )
}
