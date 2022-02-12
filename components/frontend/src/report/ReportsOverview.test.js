import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { ReportsOverview } from './ReportsOverview';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

function render_reports_overview(reports, reportsOverview, reportDate) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <ReportsOverview reports={reports} reports_overview={reportsOverview} report_date={reportDate || null} />
        </Permissions.Provider>
    )
}

it('shows an error message if there are no reports at the specified date', () => {
    render_reports_overview([], {}, "today")
    expect(screen.getAllByText(/Sorry, no reports existed at today/).length).toBe(1);
});

it('shows the reports overview', () => {
    const reports = [{ summary: { red: 0, green: 0, yellow: 0, grey: 0, white: 0 }, summary_by_tag: {} }]
    const reportsOverview = { title: "Overview", permissions: {} }
    render_reports_overview(reports, reportsOverview)
    expect(screen.getAllByText(/Overview/).length).toBe(1);
});

it('shows the comment', () => {
    const reports = [{ summary: { red: 0, green: 0, yellow: 0, grey: 0, white: 0 }, summary_by_tag: {} }]
    const reportsOverview = { title: "Overview", comment: "Commentary", permissions: {} }
    render_reports_overview(reports, reportsOverview)
    expect(screen.getAllByText(/Commentary/).length).toBe(1);
});

it('shows the report tag cards', () => {
    const reports = [{ summary: { red: 0, green: 0, yellow: 0, grey: 0, white: 0 }, summary_by_tag: { Tag: { red: 1 } } }]
    const reportsOverview = { title: "Overview", permissions: {} }
    render_reports_overview(reports, reportsOverview)
    expect(screen.getAllByText(/Tag/).length).toBe(1);
});

it('adds a report', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_reports_overview([], {})
        fireEvent.click(screen.getByText(/Add report/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/new", {});
});

it('copies a report', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    const reports = [{ report_uuid: "uuid", title: "Existing report", summary: { red: 0, green: 0, yellow: 0, grey: 0, white: 0 }, summary_by_tag: {} }]
    await act(async () => {
        render_reports_overview(reports, {})
        fireEvent.click(screen.getByText(/Copy report/));
    });
    await act(async () => {
        fireEvent.click(screen.getByRole("option"));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/uuid/copy", {});
});
