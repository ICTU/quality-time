import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { Report } from './Report';
import { DataModel } from '../context/DataModel';

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

function renderReport(report, { report_date = null, hiddenColumns = [], history = mockHistory } = {}) {
    render(
        <DataModel.Provider value={datamodel}>
            <Report
                history={history}
                reports={[report]}
                report={report}
                report_date={report_date}
                hiddenColumns={hiddenColumns}
                visibleDetailsTabs={[]}
            />
        </DataModel.Provider>
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
    renderReport(report, { hiddenColumns: ["status"]})
    expect(screen.queryByText(/Status/)).toBe(null)
});

it('sorts the column', async () => {
    let replace = jest.fn()
    let history = { location: {}, replace: replace };
    renderReport(report, {history: history})
    fireEvent.click(screen.getByText(/Tags/))
    expect(replace).toHaveBeenCalledWith({ search: "?sort_column=tags" })
});

it('sorts the column descending', async () => {
    let replace = jest.fn()
    let history = { location: { search: "?sort_column=tags" }, replace: replace };
    renderReport(report, {history: history})
    fireEvent.click(screen.getByText(/Tags/))
    expect(replace).toHaveBeenCalledWith({ search: "?sort_column=tags&sort_direction=descending" })
});

it('stops sorting', async () => {
    let replace = jest.fn()
    let history = { location: { search: "?sort_column=tags&sort_direction=descending" }, replace: replace };
    renderReport(report, {history: history})
    fireEvent.click(screen.getByText(/Tags/))
    expect(replace).toHaveBeenCalledWith({ search: "?sort_direction=descending" })
});

it('sorts another column', async () => {
    let replace = jest.fn()
    let history = { location: { search: "?sort_column=tags" }, replace: replace };
    renderReport(report, {history: history})
    fireEvent.click(screen.getByText(/Comment/))
    expect(replace).toHaveBeenCalledWith({ search: "?sort_column=comment" })
});
