import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import * as fetch_server_api from '../api/fetch_server_api';
import { Report } from './Report';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';

jest.mock('../api/fetch_server_api', () => {
    const originalModule = jest.requireActual('../api/fetch_server_api');

    return {
        __esModule: true,
        ...originalModule,
        fetch_server_api: jest.fn().mockResolvedValue({ ok: true, measurements: [] }),
    };
});

beforeEach(() => {
    jest.clearAllMocks();
});

const datamodel = {
    subjects: {
        subject_type: { name: "Subject type", metrics: ['metric_type'] }
    },
    metrics: {
        metric_type: { name: "Metric type", tags: [] }
    }
}
const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            type: "subject_type", name: "Subject title", metrics: {
                metric_uuid: { name: "Metric name", type: "metric_type", tags: ["tag"], recent_measurements: [] },
                another_metric_uuid: { name: "Metric name", type: "metric_type", tags: [], recent_measurements: [] },
            }
        }
    }
};

function renderReport(reportToRender, { dates = [new Date()], report_date = null, hiddenColumns = [], handleSort = null, sortColumn = null, sortDirection = "ascending" } = {}) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <Report
                    dates={dates}
                    reports={[reportToRender]}
                    report={reportToRender}
                    report_date={report_date}
                    hiddenColumns={hiddenColumns}
                    handleSort={handleSort}
                    sortColumn={sortColumn}
                    sortDirection={sortDirection}
                    visibleDetailsTabs={[]}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('shows the report', async () => {
    await act(async () => renderReport(report))
    expect(screen.getAllByText(/Subject title/).length).toBe(2)  // Once as dashboard card and once as subject header
});

it('shows an error message if there is no report', () => {
    renderReport(null)
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
});

it('shows an error message if there was no report', () => {
    renderReport(null, { report_date: new Date("2020-01-01") })
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
});

it('hides columns on load', async () => {
    await act(async () => renderReport(report, { hiddenColumns: ["status"] }))
    expect(screen.queryByText(/Status/)).toBe(null)
});

it('sorts the column', async () => {
    let handleSort = jest.fn();
    await act(async () => renderReport(report, { handleSort: handleSort }))
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
});

it('sorts the column descending', async () => {
    let handleSort = jest.fn();
    await act(async () => renderReport(report, { sortColumn: "comment", handleSort: handleSort }))
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
});

it('stops sorting', async () => {
    let handleSort = jest.fn();
    await act(async () => renderReport(report, { sortColumn: "issues", sortDirection: "descending", handleSort: handleSort }))
    fireEvent.click(screen.getByText(/Issues/))
    expect(handleSort).toHaveBeenCalledWith("issues")
});

it('stop sorting on add metric', async () => {
    let handleSort = jest.fn();
    await act(async () => renderReport(report, { sortColumn: "status", handleSort: handleSort }))
    await act(async () => fireEvent.click(screen.getByText(/Add metric/)))
    await act(async () => fireEvent.click(screen.getByText(/Metric type/)))
    expect(handleSort).toHaveBeenCalledWith(null)
})

it('sorts another column', async () => {
    let handleSort = jest.fn();
    await act(async () => renderReport(report, { sortColumn: "issues", handleSort: handleSort }))
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
});

it('filters by tag', async () => {
    await act(async () => renderReport(report))
    expect(screen.getAllByText(/Metric name/).length).toBe(2)
    fireEvent.click(screen.getAllByText(/tag/)[0])
    expect(screen.getAllByText(/Metric name/).length).toBe(1)
});

it('fetches measurements if nr dates > 1', async () => {
    await act(async () => { renderReport(report, { dates: [new Date(Date.UTC(2022, 3, 25)), new Date(Date.UTC(2022, 3, 28))] }) });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "report/report_uuid/measurements?min_report_date=2022-04-25T00:00:00.000Z");
})

it('fetches measurements if nr dates > 1 and time traveling', async () => {
    await act(async () => { renderReport(report, { dates: [new Date(Date.UTC(2022, 3, 25)), new Date(Date.UTC(2022, 3, 26))], report_date: new Date(Date.UTC(2022, 3, 26)) }) });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "report/report_uuid/measurements?report_date=2022-04-26T00:00:00.000Z&min_report_date=2022-04-25T00:00:00.000Z");
})

it('fetches measurements if nr dates == 1', async () => {
    await act(async () => { renderReport(report, { dates: [new Date(Date.UTC(2022, 3, 26))] }) });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "report/report_uuid/measurements?min_report_date=2022-04-26T00:00:00.000Z");
})
