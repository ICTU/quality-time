import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Target } from './Target';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const dataModel = {
    metrics: {
        violations: { unit: "violations", direction: "<", name: "Violations", default_scale: "count", scales: ["count", "percentage"] },
        violations_with_default_target: { target: "100", unit: "violations", direction: "<", name: "Violations", default_scale: "count", scales: ["count", "percentage"] },
        source_version: { unit: "", direction: "<", name: "Source version", default_scale: "version_number", scales: ["version_number"] }
    }
};

function render_metric_target(metric) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Target
                    metric={metric}
                    metric_uuid="metric_uuid"
                    target_type="target"
                    label="Target"
                    reload={() => {/* Dummy implementation */ }}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('sets the metric integer target', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    render_metric_target({type: "violations", target: "10"});
    await userEvent.type(screen.getByDisplayValue("10"), '42{Enter}', {initialSelectionStart: 0, initialSelectionEnd: 2});
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/target", { target: "42" });
});

it('sets the metric version target', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    render_metric_target({type: "source_version", target: "10"});
    await userEvent.type(screen.getByDisplayValue("10"), '4.2{Enter}', {initialSelectionStart: 0, initialSelectionEnd: 2});
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/target", { target: "4.2" });
});

it('displays the default target if changed', () => {
    render_metric_target({type: "violations_with_default_target"});
    expect(screen.queryAllByText(/default:/).length).toBe(1);
});

it('shows help', async () => {
    render_metric_target({type: "violations", target: "10", near_target: "15"});
    await userEvent.tab()
    await waitFor(() => { expect(screen.queryAllByText(/How measurement values are evaluated/).length).toBe(1) });
})

function assertVisible(...matchers) {
    matchers.forEach((matcher) => expect(screen.queryAllByText(matcher).length).toBe(1))
}

function assertNotVisible(...matchers) {
    matchers.forEach((matcher) => expect(screen.queryAllByText(matcher).length).toBe(0))
}

it('shows help for evaluated metric without tech debt', async () => {
    render_metric_target({type: "violations", target: "10", near_target: "15"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target met/, /≦ 10 violations/, /Near target met/, /10 - 15 violations/, /Target not met/, /> 15 violations/)
        assertNotVisible(/Debt target met/)
    });
})

it('shows help for evaluated metric with tech debt', async () => {
    render_metric_target({type: "violations", target: "10", debt_target: "15", near_target: "20", accept_debt: true});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target met/, /≦ 10 violations/, /Debt target met/, /10 - 15 violations/, /Near target met/, /15 - 20 violations/, /Target not met/, /> 20 violations/)
    });
})

it('shows help for evaluated metric with tech debt with end date', async () => {
    render_metric_target({type: "violations", target: "10", debt_target: "15", near_target: "20", accept_debt: true, debt_end_date: "3000-01-01"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target met/, /≦ 10 violations/, /Debt target met/, /10 - 15 violations/, /Near target met/, /15 - 20 violations/, /Target not met/, /> 20 violations/)
    });
})

it('shows help for evaluated metric with tech debt with end date in the past', async () => {
    render_metric_target({type: "violations", target: "10", debt_target: "15", near_target: "20", accept_debt: true, debt_end_date: "2000-01-01"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target met/, /≦ 10 violations/, /Near target met/, /10 - 20 violations/, /Target not met/, /> 20 violations/)
        assertNotVisible(/Debt target met/)
    });
})

it('shows help for evaluated metric with tech debt completely overlapping near target', async () => {
    render_metric_target({type: "violations", target: "10", debt_target: "20", near_target: "20", accept_debt: true});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target met/, /≦ 10 violations/, /Debt target met/, /10 - 20 violations/, /Target not met/, /> 20 violations/)
        assertNotVisible(/Near target met/)
    });
})

it('shows help for evaluated metric without tech debt and target completely overlapping near target', async () => {
    render_metric_target({type: "violations", target: "10", near_target: "10"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target met/, /≦ 10 violations/, /Target not met/, /> 10 violations/)
        assertNotVisible(/Debt target met/, /Near target met/)
    });
})

it('shows help for evaluated more-is-better metric without tech debt', async () => {
    render_metric_target({type: "violations", target: "15", near_target: "10", direction: ">"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target not met/, /< 10 violations/, /Near target met/, /10 - 15 violations/, /Target met/, /≧ 15 violations/)
        assertNotVisible(/Debt target met/)
    });
})

it('shows help for evaluated more-is-better metric with tech debt', async () => {
    render_metric_target({type: "violations", target: "15", near_target: "5", debt_target: "10", accept_debt: true, direction: ">"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target not met/, /< 5 violations/, /Near target met/, /5 - 10 violations/, /Debt target met/, /10 - 15 violations/, /Target met/, /≧ 15 violations/)
    });
})

it('shows help for evaluated more-is-better metric with tech debt completely overlapping near target', async () => {
    render_metric_target({type: "violations", target: "15", near_target: "5", debt_target: "5", accept_debt: true, direction: ">"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target not met/, /< 5 violations/, /Debt target met/, /5 - 15 violations/, /Target met/, /≧ 15 violations/)
        assertNotVisible(/Near target met/)
    });
})

it('shows help for evaluated more-is-better metric without tech debt and target completely overlapping near target', async () => {
    render_metric_target({type: "violations", target: "15", near_target: "15", direction: ">"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target not met/, /< 15 violations/, /Target met/, /≧ 15 violations/)
        assertNotVisible(/Near target met/, /Debt target met/)
    });
})

it('shows help for evaluated metric without tech debt and zero target completely overlapping near target', async () => {
    render_metric_target({type: "violations", target: "0", near_target: "0", direction: ">"});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Target met/, /≧ 0 violations/)
        assertNotVisible(/Debt target met/, /Near target met/, /Target not met/)
    });
})

it('shows help for informative metric', async () => {
    render_metric_target({type: "violations", evaluate_targets: false});
    await userEvent.tab()
    await waitFor(() => {
        assertVisible(/Informative/, /violations are not evaluated/)
        assertNotVisible(/Target met/, /Debt target met/, /Near target met/, /Target not met/)
    });
})
