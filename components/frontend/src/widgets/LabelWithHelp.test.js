import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LabelWithHelp } from './LabelWithHelp';

it("shows the label", () => {
    render(<LabelWithHelp label="Hello" />)
    expect(screen.getByText(/Hello/)).not.toBe(null)
})

it("shows the help", async () => {
    render(<LabelWithHelp label="Hello" help="Help" />)
    await userEvent.hover(screen.queryByTestId("help-icon"))
    await waitFor(() => {
        expect(screen.queryByText(/Help/)).not.toBe(null)
    })
})
