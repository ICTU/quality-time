import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { ReportsOverview } from './ReportsOverview';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import * as fetch_server_api from '../api/fetch_server_api';
import { mockGetAnimations } from '../dashboard/MockAnimations';

beforeEach(() => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    mockGetAnimations()
})

afterEach(() => jest.restoreAllMocks());

function render_reports_overview(reports, reportsOverview, reportDate) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <ReportsOverview
                dates={[reportDate || new Date()]}
                measurements={[{ status: "target_met" }]}
                report_date={reportDate || null}
                reports={reports}
                reports_overview={reportsOverview}
            />
        </Permissions.Provider>
    )
}

it('shows an error message if there are no reports at the specified date', async () => {
    await act(async () => render_reports_overview([], {}, new Date()))
    expect(screen.getAllByText(/Sorry, no reports existed at/).length).toBe(1);
});

it('shows the reports overview', async () => {
    const reports = [{ subjects: {} }]
    const reportsOverview = { title: "Overview", permissions: {} }
    await act(async () => render_reports_overview(reports, reportsOverview, new Date()))
    expect(screen.getAllByText(/Overview/).length).toBe(1);
});

it('shows the comment', async () => {
    const reports = [{ subjects: {} }]
    const reportsOverview = { title: "Overview", comment: "Commentary", permissions: {} }
    await act(async () => render_reports_overview(reports, reportsOverview))
    expect(screen.getAllByText(/Commentary/).length).toBe(1);
});

it('shows the report tag cards', async () => {
    const reports = [{ subjects: { subject_uuid: { metrics: { metric_uuid: { tags: ["Tag"] } } } } }]
    const reportsOverview = { title: "Overview", permissions: {} }
    await act(async () => render_reports_overview(reports, reportsOverview))
    expect(screen.getAllByText(/Tag/).length).toBe(1);
});

it('adds a report', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => render_reports_overview([], {}));
    fireEvent.click(screen.getByText(/Add report/));
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/new", {});
});

it('copies a report', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    const reports = [{ report_uuid: "uuid", subjects: {}, title: "Existing report" }]
    await act(async () => render_reports_overview(reports, {}))
    fireEvent.click(screen.getByText(/Copy report/));
    await act(async () => { fireEvent.click(screen.getByRole("option")); });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/uuid/copy", {});
});
