import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EDIT_ENTITY_PERMISSION, Permissions } from '../context/Permissions';
import * as source from '../api/source';
import { SourceEntityDetails } from './SourceEntityDetails';

jest.mock("../api/source.js")

function reload() {
    /* Dummy implementation */
}

function renderSourceEntityDetails() {
    render(
        <Permissions.Provider value={[EDIT_ENTITY_PERMISSION]}>
            <SourceEntityDetails
                metric_uuid="metric_uuid"
                source_uuid="source_uuid"
                entity={{ key: "key" }}
                status="unconfirmed"
                name="violation"
                reload={reload}
            />
        </Permissions.Provider>
    )
}

it('changes the entity status', () => {
    source.set_source_entity_attribute = jest.fn()
    renderSourceEntityDetails()
    fireEvent.click(screen.getByText(/Confirm/))
    expect(source.set_source_entity_attribute).toHaveBeenCalledWith(
        "metric_uuid", "source_uuid", "key", "status", "confirmed", reload
    );
})

it('changes the entity status end date', async () => {
    source.set_source_entity_attribute = jest.fn()
    renderSourceEntityDetails()
    await userEvent.type(screen.getByPlaceholderText(/YYYY-MM-DD/), '2222-01-01{Tab}', {initialSelectionStart: 0, initialSelectionEnd: 10} );
    expect(source.set_source_entity_attribute).toHaveBeenCalledWith(
        "metric_uuid", "source_uuid", "key", "status_end_date", "2222-01-01", reload
    );
})

it('changes the rationale', async () => {
    source.set_source_entity_attribute = jest.fn()
    renderSourceEntityDetails()
    await userEvent.type(screen.getByPlaceholderText(/Rationale/), 'Rationale');
    await userEvent.tab()
    expect(source.set_source_entity_attribute).toHaveBeenCalledWith(
        "metric_uuid", "source_uuid", "key", "rationale", "Rationale", reload
    );
})
