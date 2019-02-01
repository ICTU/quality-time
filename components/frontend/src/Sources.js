import React from 'react';
import { Table } from 'semantic-ui-react';
import { SourceType } from './SourceType';
import { SourceParameters } from './SourceParameters';


function Sources(props) {
    const sources = Object.keys(props.sources).map((source_uuid) =>
        (
            <Table.Row key={source_uuid}>
                <Table.Cell>
                    <SourceType subject_uuid={props.subject_uuid} metric_uuid={props.metric_uuid}
                        source_uuid={source_uuid} source_type={props.sources[source_uuid].type}
                        metric_type={props.metric_type} datamodel={props.datamodel} />
                </Table.Cell>
                <Table.Cell>
                    <SourceParameters subject_uuid={props.subject_uuid} metric_uuid={props.metric_uuid}
                        source_uuid={source_uuid} metric_type={props.metric_type}
                        source={props.sources[source_uuid]} datamodel={props.datamodel} />
                </Table.Cell>
            </Table.Row>
        )
    );
    return (
        <Table columns={2} size='small'>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell width={1}>Source</Table.HeaderCell>
                    <Table.HeaderCell width={10}>Parameters</Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>{sources}</Table.Body>
        </Table>
    )
}

export { Sources };