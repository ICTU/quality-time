import React from 'react';
import { render, screen } from '@testing-library/react';
import { ReportsOverview } from './ReportsOverview';

it('shows an error message if there are no reports at the specified date', () => {
    render(<ReportsOverview reports={[]} report_date="today" />);
    expect(screen.getAllByText(/Sorry, no reports existed at today/).length).toBe(1);
});

it('shows the reports overview', () => {
    render(
        <ReportsOverview
            reports={[{ summary: { red: 0, green: 0, yellow: 0, grey: 0, white: 0 }, summary_by_tag: {} }]}
            reports_overview={{ title: "Overview", permissions: {} }}
        />
    );
    expect(screen.getAllByText(/Overview/).length).toBe(1);
});

it('shows the report tag cards', () => {
    render(
        <ReportsOverview
            reports={[{ summary: { red: 0, green: 0, yellow: 0, grey: 0, white: 0 }, summary_by_tag: { Tag: { red: 1 } } }]}
            reports_overview={{ title: "Overview", permissions: {} }}
        />
    );
    expect(screen.getAllByText(/Tag/).length).toBe(1);
});