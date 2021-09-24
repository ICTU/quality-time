import React from 'react';
import { render, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StatusIcon } from './StatusIcon';

it("renders a checkmark if the status is target met", () => {
    const { getAllByLabelText } = render(<StatusIcon status="target_met" />)
    expect(getAllByLabelText(/Target met/).length).toBe(1)
})

it("renders a question mark if the status is missing", () => {
    const { getAllByLabelText } = render(<StatusIcon />)
    expect(getAllByLabelText(/Unknown/).length).toBe(1)
})

it("renders a popup with the date the status started", async () => {
    let startDate = new Date();
    startDate.setDate(startDate.getDate() - 4);
    const { queryByLabelText, queryByText } = render(<StatusIcon status="target_met" status_start={startDate} />)
    userEvent.hover(queryByLabelText(/Target met/))
    await waitFor(() => { expect(queryByText("4 days ago")).not.toBe(null) })
})