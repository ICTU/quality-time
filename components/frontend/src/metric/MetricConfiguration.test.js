import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { MetricConfiguration } from './MetricConfiguration';
import * as changelog_api from '../api/changelog';

jest.mock("../api/changelog.js");

const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            name: "Metric",
            metrics: {
                metric_uuid: {
                    accept_debt: false,
                    tags: [],
                    type: "violations",
                    sources: {}
                }
            }
        }
    }
};

const dataModel = {
    sources: { source_type: { name: "The source", parameters: {}, entities: { violations: { name: "Attribute", attributes: [] } } } },
    metrics: { violations: { direction: "<", tags: [], sources: ["source_type"] } },
    subjects: { subject_type: { metrics: ["violations"] } }
}

async function renderMetricConfiguration() {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }));

    await act(async () => {
        render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <DataModel.Provider value={dataModel}>
                    <MetricConfiguration
                        metric_uuid="metric_uuid"
                        metric={report["subjects"]["subject_uuid"]["metrics"]["metric_uuid"]}
                        report={report}
                        subject={{ type: "subject_type" }}
                    />
                </DataModel.Provider>
            </Permissions.Provider>
        )
    })
}

it('loads the changelog', async () => {
    await renderMetricConfiguration();
    await act(async () => fireEvent.click(screen.getByText(/Changelog/)));
    expect(changelog_api.get_changelog).toHaveBeenCalledWith(5, { metric_uuid: "metric_uuid" });
});

it('shows the share tab', async () => {
    await renderMetricConfiguration();
    await act(async () => fireEvent.click(screen.getByText(/Share/)));
    expect(screen.getByText(/permanent link/)).not.toBe(null)
});
