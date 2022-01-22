import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { Report } from './Report';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';

let mockHistory = { location: {}, replace: () => {/* No implementatin needed */ } };
const datamodel = { subjects: { subject_type: { name: "Subject type", metrics: ['metric_type'] } }, metrics: { metric_type: { tags: [] } } }
const report = {
    report_uuid: "report_uuid",
    summary_by_subject: {
        subject_uuid: {
            red: 0,
            green: 0,
            yellow: 0,
            grey: 0,
            white: 0
        }
    },
    summary_by_tag: {
        tag: {
            red: 0,
            green: 0,
            yellow: 0,
            grey: 0,
            white: 0
        }
    },
    subjects: {
        subject_uuid: {
            type: "subject_type", name: "Subject title", metrics: {
                metric_uuid: { type: "metric_type", tags: ["tag"], recent_measurements: [] }
            }
        }
    }
};

function renderReport(reportToRender, { report_date = null, hiddenColumns = [], history = mockHistory } = {}) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <Report
                    history={history}
                    reports={[reportToRender]}
                    report={reportToRender}
                    report_date={report_date}
                    hiddenColumns={hiddenColumns}
                    visibleDetailsTabs={[]}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('shows the report', () => {
    renderReport(report)
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
    mockHistory.location.search = "?hidden_columns=status"
    renderReport(report, { hiddenColumns: ["status"] })
    expect(screen.queryByText(/Status/)).toBe(null)
});

it('sorts the column', async () => {
    let history = { location: {}, replace: jest.fn() };
    renderReport(report, { history: history })
    fireEvent.click(screen.getByText(/Tags/))
    expect(history.replace).toHaveBeenCalledWith({ search: "?sort_column=tags" })
});

it('sorts the column descending', async () => {
    let history = { location: { search: "?sort_column=comment" }, replace: jest.fn() };
    renderReport(report, { history: history })
    fireEvent.click(screen.getByText(/Comment/))
    expect(history.replace).toHaveBeenCalledWith({ search: "?sort_column=comment&sort_direction=descending" })
});

it('stops sorting', async () => {
    let history = { location: { search: "?sort_column=issues&sort_direction=descending" }, replace: jest.fn() };
    renderReport(report, { history: history })
    fireEvent.click(screen.getByText(/Issues/))
    expect(history.replace).toHaveBeenCalledWith({ search: "?sort_direction=descending" })
});

it('stop sorting on add metric', async () => {
    let history = { location: { search: "?sort_column=measurement&sort_direction=descending" }, replace: jest.fn() };
    renderReport(report, { history: history })
    await act(async () => fireEvent.click(screen.getByText(/Add metric/)))
    expect(history.replace).toHaveBeenCalledWith({ search: "?sort_direction=descending" })
})

it('sorts another column', async () => {
    let history = { location: { search: "?sort_column=tags" }, replace: jest.fn() };
    renderReport(report, { history: history })
    fireEvent.click(screen.getByText(/Comment/))
    expect(history.replace).toHaveBeenCalledWith({ search: "?sort_column=comment" })
});
