import React from 'react';
import { render, screen } from '@testing-library/react';
import { TimeLeft } from './TimeLeft';

it("does not render the time left if the status does not demand action", () => {
    render(<TimeLeft metric={{ status: "target_met" }} report={{}} />)
    expect(screen.queryAllByText(/day/).length).toBe(0)
})

it("does not render the time left if there is no status start date", () => {
    render(<TimeLeft metric={{ status: "target_not_met" }} report={{}} />)
    expect(screen.queryAllByText(/day/).length).toBe(0)
})

it("renders 0 days left if the deadline is in the past", () => {
    render(<TimeLeft metric={{ status: "target_not_met", status_start: "2022-01-01" }} report={{}} />)
    expect(screen.queryAllByText(/0 days/).length).toBe(1)
})

it("renders the time left if status demands action", () => {
    const now = new Date()
    render(<TimeLeft metric={{ status: "target_not_met", status_start: now.toISOString() }} report={{}} />)
    expect(screen.queryAllByText(/days/).length).toBe(1)
})
