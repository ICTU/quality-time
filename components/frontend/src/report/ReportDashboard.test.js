import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { ReportDashboard } from './ReportDashboard';
import { mockGetAnimations } from '../dashboard/MockAnimations';

beforeEach(() => {
    mockGetAnimations()
});

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

function renderDashboard(
    {
        hiddenTags = [],
        dates = [new Date()],
        onClick = jest.fn(),
        reportToRender = null,
    } = {}
) {
    return render(
        <div id="dashboard">
            <ReportDashboard dates={dates} hiddenTags={hiddenTags} onClick={onClick} report={reportToRender} />
        </div>
    )
}

it('shows the dashboard', async () => {
    renderDashboard({ reportToRender: report })
    expect(screen.getAllByText(/Subject title/).length).toBe(1)
    expect(screen.getAllByText(/tag/).length).toBe(1)
    expect(screen.getAllByText(/other/).length).toBe(1)
});

it('hides tags', async () => {
    renderDashboard({ reportToRender: report, hiddenTags: ["other"] })
    expect(screen.getAllByText(/Subject title/).length).toBe(1)
    expect(screen.getAllByText(/tag/).length).toBe(1)
    expect(screen.queryAllByText(/other/).length).toBe(0)
});

it('hides a subject if all its tags are hidden', async () => {
    renderDashboard({ reportToRender: report, hiddenTags: ["other", "tag"] })
    expect(screen.queryAllByText(/Subject title/).length).toBe(0)
    expect(screen.queryAllByText(/tag/).length).toBe(0)
    expect(screen.queryAllByText(/other/).length).toBe(0)
});

it('calls the callback on click', async () => {
    const onClick = jest.fn()
    renderDashboard({ reportToRender: report, onClick: onClick })
    fireEvent.click(screen.getByText(/Subject title/))
    expect(onClick).toHaveBeenCalledWith(expect.anything(), "subject_uuid")
});
