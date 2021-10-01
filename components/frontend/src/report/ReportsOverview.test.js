import React from 'react';
import { render, screen } from '@testing-library/react';
import { ReportsOverview } from './ReportsOverview';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';

function render_reports_overview(reports, reportsOverview) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <ReportsOverview reports={reports} reports_overview={reportsOverview} report_date="today" />
        </Permissions.Provider>
    )
}

it('shows an error message if there are no reports at the specified date', () => {
    render_reports_overview([])
    expect(screen.getAllByText(/Sorry, no reports existed at today/).length).toBe(1);
});

it('shows the reports overview', () => {
    const reports = [{ summary: { red: 0, green: 0, yellow: 0, grey: 0, white: 0 }, summary_by_tag: {} }]
    const reportsOverview= { title: "Overview", permissions: {} }
    render_reports_overview(reports, reportsOverview)
    expect(screen.getAllByText(/Overview/).length).toBe(1);
});

it('shows the report tag cards', () => {
    const reports= [{ summary: { red: 0, green: 0, yellow: 0, grey: 0, white: 0 }, summary_by_tag: { Tag: { red: 1 } } }]
    const reportsOverview= { title: "Overview", permissions: {} }
    render_reports_overview(reports, reportsOverview)
    expect(screen.getAllByText(/Tag/).length).toBe(1);
});
