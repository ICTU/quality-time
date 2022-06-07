import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { SourceType } from './SourceType';

jest.mock("../api/fetch_server_api.js")

const data_model = {
    metrics: {
        violations: {
            sources: ["sonarqube", "gitlab"],
            unit: "violations",
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count"]
        },
    },
    sources: {
        sonarqube: {
            name: "SonarQube"
        },
        gitlab: {
            name: "GitLab"
        },
        unsupported: {
            name: "Unsupported"
        }
    }
};

function render_source_type(metricType, sourceType, mockSetSourceAttribute) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={data_model}>
                <SourceType
                    metric_type={metricType}
                    source_type={sourceType}
                    set_source_attribute={mockSetSourceAttribute}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('sets the source type', async () => {
    const mockSetSourceAttribute = jest.fn()
    await act(async () => { render_source_type("violations", "sonarqube", mockSetSourceAttribute) });
    await userEvent.type(screen.getByRole("combobox"), 'GitLab{Enter}');
    expect(mockSetSourceAttribute).toHaveBeenLastCalledWith("type", "gitlab")
});

it('shows the metric type even when not supported by the subject type', async () => {
    await act(async () => { render_source_type("violations", "unsupported") });
    expect(screen.queryAllByText(/Unsupported/).length).toBe(2)
});
