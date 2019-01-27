import React from 'react';
import { Table } from 'semantic-ui-react';

function SourceTable(props) {
    const sources = props.sources.map((source) =>
        (
            <Table.Row key={source.api_url}>
                <Table.Cell>{source.name}</Table.Cell>
                <Table.Cell>{source.api_url}</Table.Cell>
                <Table.Cell> ... </Table.Cell>
            </Table.Row>
        )
    );

    return (
        <Table columns={3}>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell>Source</Table.HeaderCell>
                    <Table.HeaderCell>URL</Table.HeaderCell>
                    <Table.HeaderCell>Extra information</Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>{sources}</Table.Body>
        </Table>
    )
}

export { SourceTable };