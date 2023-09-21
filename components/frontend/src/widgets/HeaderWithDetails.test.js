import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HeaderWithDetails } from './HeaderWithDetails';

it('expands and collapses the details on click', () => {
    render(<HeaderWithDetails><p>Hello</p></HeaderWithDetails>)
    expect(screen.queryAllByText("Hello").length).toBe(0)
    fireEvent.click(screen.getByTitle("expand"))
    expect(screen.getAllByText("Hello").length).toBe(1)
    fireEvent.click(screen.getByTitle("expand"))
    expect(screen.queryAllByText("Hello").length).toBe(0)
})

it('expands and collapses the details on space', async () => {
    render(<HeaderWithDetails header="Header"><p>Hello</p></HeaderWithDetails>)
    expect(screen.queryAllByText("Hello").length).toBe(0)
    await userEvent.tab()
    await userEvent.keyboard(" ")
    expect(screen.getAllByText("Hello").length).toBe(1)
    await userEvent.keyboard(" ")
    expect(screen.queryAllByText("Hello").length).toBe(0)
})
