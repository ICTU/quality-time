import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import history from 'history/browser';
import { mockGetAnimations } from '../dashboard/MockAnimations';
import { ReportsOverviewDashboard } from './ReportsOverviewDashboard';

beforeEach(() => {
    mockGetAnimations()
    history.push("")
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
    },
    title: "Report"
};

function renderReportsOverviewDashboard(
    {
        dates = [new Date()],
        openReport = null,
        reports = [report],
    } = {}
) {
    render(
        <div id="dashboard">
            <ReportsOverviewDashboard
                dates={dates}
                hiddenTags={[]}
                openReport={openReport}
                reports={reports}
            />
        </div>
    )
}

it('shows the reports overview dashboard', async () => {
    const reports = [{ subjects: {} }]
    renderReportsOverviewDashboard()
    expect(screen.getAllByText(/Legend/).length).toBe(1);
});

it('calls the callback on click', async () => {
    const openReport = jest.fn()
    renderReportsOverviewDashboard({ openReport: openReport })
    fireEvent.click(screen.getByText(/Report/))
    expect(openReport).toHaveBeenCalledWith("report_uuid")
});
