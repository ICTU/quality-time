import React from 'react';
import { Table } from 'semantic-ui-react';
import { render, screen } from '@testing-library/react';
import { SubjectTableHeader } from './SubjectTableHeader';

it('shows the column dates and unit', () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    render(
        <Table>
            <SubjectTableHeader
                columnDates={[date1, date2]}
                nrDates={2}
                hiddenColumns={[]}
            />
        </Table>
    );
    [date1.toLocaleDateString(), date2.toLocaleDateString(), "Unit", "Source", "Comment", "Issues", "Tags"].forEach(
        header => expect(screen.getAllByText(header).length).toBe(1)
    );
    ["Trend (7 days)", "Status", "Measurement", "Target"].forEach(
        header => expect(screen.queryAllByText(header).length).toBe(0)
    )
})

it('does not show the column dates and unit', () => {
    const date1 = new Date("2022-02-02")
    const date2 = new Date("2022-02-03")
    render(
        <Table>
            <SubjectTableHeader
                columnDates={[date1, date2]}
                nrDates={1}
                hiddenColumns={[]}
            />
        </Table>
    );
    [date1.toLocaleDateString(), date2.toLocaleDateString(), "Unit"].forEach(
        header => expect(screen.queryAllByText(header).length).toBe(0)
    );
    ["Trend (7 days)", "Status", "Measurement", "Target", "Source", "Comment", "Issues", "Tags"].forEach(
        header => expect(screen.queryAllByText(header).length).toBe(1)
    );
})

it('hides columns', () => {
    render(
        <Table>
            <SubjectTableHeader
                columnDates={[]}
                nrDates={1}
                hiddenColumns={["trend", "status", "measurement", "target", "source", "comment", "issues", "tags"]}
            />
        </Table>
    );
    ["Trend (7 days)", "Status", "Measurement", "Target", "Source", "Comment", "Issues", "Tags"].forEach(
        header => expect(screen.queryAllByText(header).length).toBe(0)
    );
})
