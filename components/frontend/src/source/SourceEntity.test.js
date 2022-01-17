import React from 'react';
import { Table } from 'semantic-ui-react';
import { fireEvent, render, screen } from '@testing-library/react';
import { SourceEntity } from './SourceEntity';

function renderSourceEntity({ status = "unconfirmed", hide_ignored_entities = false }) {
    return render(
        <Table>
            <Table.Body>
                <SourceEntity
                    status={status}
                    hide_ignored_entities={hide_ignored_entities}
                    entity_attributes={[{key: "attr1"}, {key: "attr2", color: {bad: "warning"}}]}
                    entity={{ attr1: "good", attr2: "bad" }}
                    entity_name="entity"
                />
            </Table.Body>
        </Table>
    )
}

it('renders the unconfirmed status', () => {
    renderSourceEntity({ });
    fireEvent.click(screen.getByRole("button"))
    expect(screen.getAllByText(/Unconfirmed/).length).toBe(1);
    expect(screen.getByText(/Unconfirmed/).closest("tr").className).toContain("warning_status")
})

it('renders the fixed status', () => {
    renderSourceEntity({ status: "fixed" });
    expect(screen.getAllByText(/Fixed/).length).toBe(1);
})

it('renders nothing if the status is to be ignored', () => {
    renderSourceEntity({ status: "fixed", hide_ignored_entities: true });
    expect(screen.queryAllByText(/Fixed/).length).toBe(0);
})
