import React from 'react';
import { render, screen } from '@testing-library/react';
import { Footer } from './Footer';

it('renders the report title when there is a report', () => {
    const last_update = new Date();
    render(<Footer report={{ title: "Report title" }} last_update={last_update} />)
    expect(screen.findByText("Report")).not.toBe(null)
})

it('renders a quote when there is no report', () => {
    render(<Footer />);
    expect(screen.queryByText("Report")).toBe(null)
})

it('renders a link to the report url', () => {
    render(<Footer report={{ title: "Report title" }} />)
    expect(screen.getByText("Report title").closest('a')).toHaveAttribute('href', 'http://localhost/')
})

it('renders a link to the report url from the search parameter', () => {
    Object.defineProperty(window, 'location', { value: { search: '' } });
    window.location.search = "?report_url=https://report/"
    render(<Footer report={{ title: "Report title" }} />)
    expect(screen.getByText("Report title").closest('a')).toHaveAttribute('href', 'https://report/')
})
