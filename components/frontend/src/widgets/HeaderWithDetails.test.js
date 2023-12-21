import React from 'react';
import history from 'history/browser';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HeaderWithDetails } from './HeaderWithDetails';
import { createTestableSettings } from '../__fixtures__/fixtures';

beforeEach(() => {
    history.push("")
});

it('expands the details on click', () => {
    render(<HeaderWithDetails item_uuid="uuid" settings={createTestableSettings()}><p>Hello</p></HeaderWithDetails>)
    expect(screen.queryAllByText("Hello").length).toBe(0)
    fireEvent.click(screen.getByTitle("expand"))
    expect(history.location.search).toBe("?expanded=uuid")
})

it('expands the details on space', async () => {
    render(<HeaderWithDetails header="Header" item_uuid="uuid" settings={createTestableSettings()}><p>Hello</p></HeaderWithDetails>)
    expect(screen.queryAllByText("Hello").length).toBe(0)
    await userEvent.tab()
    await userEvent.keyboard(" ")
    expect(history.location.search).toBe("?expanded=uuid")
})

it('is expanded on load when listed in the query string', () => {
    history.push("?expanded=uuid")
    render(<HeaderWithDetails header="Header" item_uuid="uuid" settings={createTestableSettings()}><p>Hello</p></HeaderWithDetails>)
    expect(screen.getAllByText("Hello").length).toBe(1)
})
