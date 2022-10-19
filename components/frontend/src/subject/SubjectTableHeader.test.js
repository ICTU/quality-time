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
                hiddenColumns={[]}
            />
        </Table>
    );
    [date1.toLocaleDateString(), date2.toLocaleDateString(), "Unit", "Sources", "Time left", "Overrun", "Comment", "Issues", "Tags"].forEach(
        header => expect(screen.getAllByText(header).length).toBe(1)
    );
    ["Trend (7 days)", "Status", "Measurement", "Target"].forEach(
        header => expect(screen.queryAllByText(header).length).toBe(0)
    )
})

it('does not show the column dates', () => {
    const date1 = new Date("2022-02-02")
    render(
        <Table>
            <SubjectTableHeader
                columnDates={[date1]}
                hiddenColumns={[]}
            />
        </Table>
    );
    [date1.toLocaleDateString(), "Overrun"].forEach(
        header => expect(screen.queryAllByText(header).length).toBe(0)
    );
    ["Trend (7 days)", "Status", "Measurement", "Target", "Unit", "Sources", "Time left", "Comment", "Issues", "Tags"].forEach(
        header => expect(screen.queryAllByText(header).length).toBe(1)
    );
})

it('hides columns', () => {
    const date1 = new Date("2022-02-02")
    render(
        <Table>
            <SubjectTableHeader
                columnDates={[date1]}
                hiddenColumns={["trend", "status", "measurement", "target", "source", "comment", "issues", "tags"]}
            />
        </Table>
    );
    ["Trend (7 days)", "Status", "Measurement", "Target", "Sources", "Comment", "Issues", "Tags"].forEach(
        header => expect(screen.queryAllByText(header).length).toBe(0)
    );
})
