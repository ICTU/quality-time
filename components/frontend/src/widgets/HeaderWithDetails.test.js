import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { HeaderWithDetails } from './HeaderWithDetails';

it('expands and collapses the details on click', () => {
    render(<HeaderWithDetails><p>Hello</p></HeaderWithDetails>)
    expect(screen.queryAllByText("Hello").length).toBe(0)
    fireEvent.click(screen.getByTitle("expand"))
    expect(screen.getAllByText("Hello").length).toBe(1)
    fireEvent.click(screen.getByTitle("expand"))
    expect(screen.queryAllByText("Hello").length).toBe(0)
})
