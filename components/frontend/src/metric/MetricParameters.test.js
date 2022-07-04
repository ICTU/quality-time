import React from 'react';
import { act, waitFor, render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { MetricParameters } from './MetricParameters';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

const data_model = {
    subjects: {
        subject_type: {
            metrics: ["violations", "source_version"]
        }
    },
    metrics: {
        violations: { unit: "violations", direction: "<", name: "Violations", default_scale: "count", scales: ["count", "percentage"] },
        source_version: { unit: "", direction: "<", name: "Source version", default_scale: "version_number", scales: ["version_number"] }
    }
};

const reportWithIssueTracker = { issue_tracker: { type: "Jira", parameters: { url: "https://jira", project_key: "KEY", issue_type: "Bug" } } }

function render_metric_parameters(scale = "count", issue_ids = [], report = { summary_by_tag: {} }, permissions=[EDIT_REPORT_PERMISSION]) {
    render(
        <Permissions.Provider value={permissions}>
            <DataModel.Provider value={data_model}>
                <MetricParameters
                    subject={{ type: "subject_type" }}
                    metric={{ type: "violations", tags: [], accept_debt: false, scale: scale, issue_ids: issue_ids }}
                    metric_uuid="metric_uuid"
                    reload={() => {/* Dummy implementation */ }}
                    report={report}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('sets the metric name', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_metric_parameters() });
    await userEvent.type(screen.getByLabelText(/Metric name/), 'New metric name{Enter}', { initialSelectionStart: 0, initialSelectionEnd: 11 });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/name", { name: "New metric name" });
});

it('sets the metric unit for metrics with the count scale', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_metric_parameters() });
    await userEvent.type(screen.getByLabelText(/Metric unit/), 'New metric unit{Enter}', { initialSelectionStart: 0, initialSelectionEnd: 11 });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/unit", { unit: "New metric unit" });
});

it('sets the metric unit field for metrics with the percentage scale', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_metric_parameters("percentage") });
    await userEvent.type(screen.getByLabelText(/Metric unit/), 'New metric unit{Enter}', { initialSelectionStart: 0, initialSelectionEnd: 11 });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/unit", { unit: "New metric unit" });
});

it('skips the metric unit field for metrics with the version number scale', () => {
    render(<DataModel.Provider value={data_model}><MetricParameters
        report={{}}
        subject={{ type: "subject_type" }}
        metric={{ type: "source_version", tags: [], accept_debt: false }}
        metric_uuid="metric_uuid"
    /></DataModel.Provider>);
    expect(screen.queryAllByText(/Metric unit/).length).toBe(0);
});

it('does not show an error message if the metric has no issues and no issue tracker is configured', async () => {
    await act(async () => { render_metric_parameters() });
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0);
});

it('does not show an error message if the metric has no issues and an issue tracker is configured', async () => {
    await act(async () => { render_metric_parameters("count", [], { issue_tracker: { type: "Jira" } }) });
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0);
});

it('does not show an error message if the metric has issues and an issue tracker is configured', async () => {
    await act(async () => { render_metric_parameters("count", ["BAR-42"], { issue_tracker: { type: "Jira", parameters: { url: "https://jira", project_key: "KEY", issue_type: "Bug" } } }) });
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0);
});

it('shows an error message if the metric has issues but no issue tracker is configured', async () => {
    await act(async () => { render_metric_parameters("count", ["FOO-42"]) });
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(1);
});

it('creates an issue', async () => {
    window.open = jest.fn()
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, error: "", issue_url: "https://tracker/foo-42" });
    await act(async () => { render_metric_parameters("count", [], reportWithIssueTracker) });
    fireEvent.click(screen.getByText(/Create new issue/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/issue/new", { metric_url: "http://localhost/#metric_uuid" });
});

it('tries to create an issue', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: false, error: "Dummy", issue_url: "" });
    await act(async () => { render_metric_parameters("count", [], reportWithIssueTracker) });
    fireEvent.click(screen.getByText(/Create new issue/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/issue/new", { metric_url: "http://localhost/#metric_uuid" });
});

it('does not show the create issue button if the user has no permissions', async () => {
    await act(async () => { render_metric_parameters("count", [], reportWithIssueTracker, []) });
    expect(screen.queryAllByText(/Create new issue/).length).toBe(0)
})

it('shows issue id suggestions', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] });
    await act(async () => { render_metric_parameters("count", [], { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } }) });
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), 'u');
    await waitFor(() => {
        expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(1);
    })
});

it('shows no issue id suggestions without a query', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] });
    await act(async () => { render_metric_parameters("count", [], { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } }) });
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), 's');
    await waitFor(() => {
        expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(1);
    })
    await userEvent.clear(screen.getByLabelText(/Issue identifiers/).firstChild);
    await waitFor(() => {
        expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(0);
    })
});

it('turns off evaluation of targets', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { render_metric_parameters() });
    await userEvent.type(screen.getByLabelText(/Evaluate metric targets/), 'No{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/evaluate_targets", { evaluate_targets: false });
});
