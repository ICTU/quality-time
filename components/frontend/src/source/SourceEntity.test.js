import React from 'react';
import { Table } from 'semantic-ui-react';
import { fireEvent, render, screen } from '@testing-library/react';
import { SourceEntity } from './SourceEntity';

function renderSourceEntity({ status = "unconfirmed", status_end_date = "", rationale = "", hide_ignored_entities = false }) {
    return render(
        <Table>
            <Table.Body>
                <SourceEntity
                    status={status}
                    status_end_date={status_end_date}
                    hide_ignored_entities={hide_ignored_entities}
                    entity_attributes={[{key: "attr1"}, {key: "attr2", color: {bad: "warning"}}]}
                    entity={{ attr1: "good", attr2: "bad" }}
                    entity_name="entity"
                    rationale={rationale}
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
    expect(screen.getAllByText(/Will be fixed/).length).toBe(1);
})

it('renders the status end date', () => {
    renderSourceEntity({ status: "fixed", status_end_date: "3000-01-01" });
    expect(screen.getAllByText(/3000-01-01/).length).toBe(1);
})

it('renders the status rationale', () => {
    renderSourceEntity({ status: "fixed", rationale: "Why?" });
    expect(screen.getAllByText(/Why\?/).length).toBe(1);
})

it('renders the status and rationale past end date', () => {
    renderSourceEntity({ status: "fixed", status_end_date: "2000-01-01", hide_ignored_entities: true, rationale: "Because" });
    expect(screen.getAllByText(/2000-01-01/).length).toBe(1);
    expect(screen.getAllByText(/Because/).length).toBe(1);
})

it('renders nothing if the status is to be ignored', () => {
    renderSourceEntity({ status: "fixed", hide_ignored_entities: true });
    expect(screen.queryAllByText(/Will be fixed/).length).toBe(0);
})
