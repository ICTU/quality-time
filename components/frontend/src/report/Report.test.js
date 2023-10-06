import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { Report } from './Report';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import * as fetch_server_api from '../api/fetch_server_api';
import { mockGetAnimations } from '../dashboard/MockAnimations';

beforeEach(() => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    mockGetAnimations()
});

afterEach(() => jest.restoreAllMocks())

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
                another_metric_uuid: { name: "Metric name", type: "metric_type", tags: ["other"], recent_measurements: [] },
            }
        }
    }
};

function renderReport(
    reportToRender,
    {
        dates = [new Date()],
        handleSort = null,
        hiddenColumns = [],
        hiddenTags = [],
        report_date = null,
        sortDirection = "ascending",
        sortColumn = null,
        toggleHiddenTag = null
    } = {}
) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <Report
                    dates={dates}
                    handleSort={handleSort}
                    hiddenColumns={hiddenColumns}
                    hiddenTags={hiddenTags}
                    measurements={[]}
                    reports={[reportToRender]}
                    report={reportToRender}
                    report_date={report_date}
                    sortDirection={sortDirection}
                    sortColumn={sortColumn}
                    toggleHiddenTag={toggleHiddenTag}
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

it('shows an error message if there is no report', async () => {
    await act(async () => renderReport(null))
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
});

it('shows an error message if there was no report', async () => {
    await act(async () => renderReport(null, { report_date: new Date("2020-01-01") }))
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

it('hides tags', async () => {
    let toggleHiddenTag = jest.fn();
    await act(async () => renderReport(report, { toggleHiddenTag: toggleHiddenTag }))
    fireEvent.click(screen.getAllByText(/tag/)[0])
    expect(toggleHiddenTag).toHaveBeenCalledWith("other")
})

it('shows hidden tags', async () => {
    let toggleHiddenTag = jest.fn();
    await act(async () => renderReport(report, { hiddenTags: ["other"], toggleHiddenTag: toggleHiddenTag }))
    expect(screen.queryAllByText("other").length).toBe(0)
    fireEvent.click(screen.getAllByText(/tag/)[0])
    expect(toggleHiddenTag).toHaveBeenCalledWith("other")
})

it('hides subjects if empty', async () => {
    await act(async () => renderReport(report, { hiddenTags: ["tag", "other"] }))
    expect(screen.queryAllByText(/Subject title/).length).toBe(0)
})
