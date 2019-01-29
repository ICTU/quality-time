import React from 'react';
import { Table } from 'semantic-ui-react';
import { SourceURL } from './SourceURL';


function SourceTable(props) {
    const sources = Object.keys(props.sources).map((source_uuid) =>
        (
            <Table.Row key={props.sources[source_uuid].url}>
                <Table.Cell>{props.sources[source_uuid].source}</Table.Cell>
                <Table.Cell>
                    <SourceURL subject_uuid={props.subject_uuid} metric_uuid={props.metric_uuid}
                        source_uuid={source_uuid} url={props.sources[source_uuid].url} />
                </Table.Cell>
            </Table.Row>
        )
    );

    return (
        <Table columns={2} size='small'>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell width={1}>Source</Table.HeaderCell>
                    <Table.HeaderCell width={10}>URL</Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>{sources}</Table.Body>
        </Table>
    )
}

export { SourceTable };