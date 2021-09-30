import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { Report } from './Report';

let mockHistory = { location: {}, replace: () => { /* No implementation needed */ } };
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

it('shows the report', () => {
    render(<Report history={mockHistory} datamodel={datamodel} reports={[report]} report={report} />);
    expect(screen.getAllByText(/Subject title/).length).toBe(2)  // Once as dashboard card and once as subject header
});

it('shows an error message if there is no report', () => {
    render(<Report history={mockHistory} />);
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
});

it('shows an error message if there was no report', () => {
    render(<Report history={mockHistory} report_date={new Date("2020-01-01")} />);
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
});

it('hides columns', () => {
    render(<Report history={mockHistory} datamodel={datamodel} reports={[report]} report={report} />);
    expect(screen.getAllByText(/Status/).length).toBe(1)
    fireEvent.click(screen.getByRole(/listbox/));
    fireEvent.click(screen.getByText(/Hide status column/));
    expect(screen.queryByText(/Status/)).toBe(null)
});

it('hides columns on load', () => {
    mockHistory.location.search = "?hidden_columns=status"
    render(<Report history={mockHistory} datamodel={datamodel} reports={[report]} report={report} />)
    expect(screen.queryByText(/Status/)).toBe(null)
    fireEvent.click(screen.getByRole(/listbox/));
    fireEvent.click(screen.getByText(/Show status column/));
    expect(screen.getAllByText(/Status/).length).toBe(1)
});

it('hides multiple columns on load', () => {
    mockHistory.location.search = "?hidden_columns=status,tags"
    render(<Report history={mockHistory} datamodel={datamodel} reports={[report]} report={report} />)
    expect(screen.queryByText(/Status/)).toBe(null)
    expect(screen.queryByText(/Tags/)).toBe(null)
    fireEvent.click(screen.getByRole(/listbox/));
    fireEvent.click(screen.getByText(/Show status column/));
    expect(screen.getAllByText(/Status/).length).toBe(1)
});

it('can handle missing columns', () => {
    mockHistory.location.search = "?hidden_columns="
    render(<Report history={mockHistory} datamodel={datamodel} reports={[report]} report={report} />)
    expect(screen.getAllByText(/Status/).length).toBe(1)
});
