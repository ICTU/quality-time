import React from 'react';
import { Table } from 'semantic-ui-react';
import { SourceURL } from './SourceURL';


function SourceTable(props) {
    const sources = props.sources.map((source, source_index) =>
        (
            <Table.Row key={source.url}>
                <Table.Cell>{source.source}</Table.Cell>
                <Table.Cell>
                    <SourceURL subject_index={props.subject_index} metric_index={props.metric_index}
                        source_index={source_index} url={source.url} />
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