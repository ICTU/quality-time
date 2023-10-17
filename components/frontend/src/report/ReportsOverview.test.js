import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import * as fetch_server_api from '../api/fetch_server_api';
import { mockGetAnimations } from '../dashboard/MockAnimations';
import { ReportsOverview } from './ReportsOverview';

beforeEach(() => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    mockGetAnimations()
})

afterEach(() => jest.restoreAllMocks());

const datamodel = {
    subjects: {
        subject_type: { name: "Subject type", metrics: ["metric_type"] }
    },
    metrics: {
        metric_type: { name: "Metric type", tags: [] }
    }
}

function render_reports_overview(reports, reportsOverview, reportDate, toggleHiddenTag, hiddenTags) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <ReportsOverview
                    dates={[reportDate || new Date()]}
                    hiddenColumns={[]}
                    hiddenTags={hiddenTags ?? []}
                    measurements={[{ status: "target_met" }]}
                    report_date={reportDate || null}
                    reports={reports}
                    reports_overview={reportsOverview}
                    toggleHiddenTag={toggleHiddenTag ?? jest.fn()}
                    visibleDetailsTabs={[]}
                />
            </DataModel.Provider>
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

const reports = [
    {
        report_uuid: "report_uuid",
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        recent_measurements: [],
                        tags: ["Foo"],
                        type: "metric_type"
                    },
                    metric_uuid2: {
                        recent_measurements: [],
                        tags: ["Bar"],
                        type: "metric_type"
                    }
                },
                type: "subject_type",
            }
        }
    }
]

const reportsOverview = { title: "Overview", permissions: {} }

it('hides the report tag cards', async () => {
    const toggleHiddenTag = jest.fn()
    await act(async () => render_reports_overview(reports, reportsOverview, new Date(), toggleHiddenTag))
    expect(screen.getAllByText(/Foo/).length).toBe(2)  // One in the dashboard, one in the table of metrics
    expect(screen.getAllByText(/Bar/).length).toBe(2)  // One in the dashboard, one in the table of metrics
    fireEvent.click(screen.getAllByText(/Foo/)[0])
    expect(toggleHiddenTag).toHaveBeenLastCalledWith("Bar")
})

it('shows the report tag cards', async () => {
    const toggleHiddenTag = jest.fn()
    await act(async () => render_reports_overview(reports, reportsOverview, new Date(), toggleHiddenTag, ["Bar"]))
    expect(screen.getAllByText(/Foo/).length).toBe(2)  // One in the dashboard, one in the table of metrics
    expect(screen.queryAllByText(/Bar/).length).toBe(0)
    fireEvent.click(screen.getAllByText(/Foo/)[0])
    expect(toggleHiddenTag).toHaveBeenLastCalledWith("Bar")
})

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
