import React from 'react';
import { act, waitFor, render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { MetricDebtParameters } from './MetricDebtParameters';
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

function renderMetricDebtParameters(scale = "count", issue_ids = [], report = { summary_by_tag: {} }, permissions=[EDIT_REPORT_PERMISSION], issue_status = []) {
    render(
        <Permissions.Provider value={permissions}>
            <DataModel.Provider value={data_model}>
                <MetricDebtParameters
                    metric={{ type: "violations", tags: [], accept_debt: false, scale: scale, issue_ids: issue_ids, issue_status: issue_status }}
                    metric_uuid="metric_uuid"
                    reload={() => {/* Dummy implementation */ }}
                    report={report}
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

it('accepts technical debt', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { renderMetricDebtParameters() });
    await userEvent.type(screen.getByLabelText(/Accept technical debt/), 'Yes{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/accept_debt", { accept_debt: true });
});

it('sets the technical debt end date', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => { renderMetricDebtParameters() });
    await userEvent.type(screen.getByPlaceholderText(/YYYY-MM-DD/), '2022-12-31{Tab}', {initialSelectionStart: 0, initialSelectionEnd: 10} );
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/debt_end_date", { debt_end_date: "2022-12-31" });
});

it('does not show an error message if the metric has no issues and no issue tracker is configured', async () => {
    await act(async () => { renderMetricDebtParameters() });
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0);
});

it('does not show an error message if the metric has no issues and an issue tracker is configured', async () => {
    await act(async () => { renderMetricDebtParameters("count", [], { issue_tracker: { type: "Jira" } }) });
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0);
});

it('does not show an error message if the metric has issues and an issue tracker is configured', async () => {
    await act(async () => { renderMetricDebtParameters("count", ["BAR-42"], { issue_tracker: { type: "Jira", parameters: { url: "https://jira", project_key: "KEY", issue_type: "Bug" } } }) });
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0);
});

it('shows an error message if the metric has issues but no issue tracker is configured', async () => {
    await act(async () => { renderMetricDebtParameters("count", ["FOO-42"]) });
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(1);
});

it('shows a connection error', async () => {
    await act(async () => { renderMetricDebtParameters("count", [], {}, [], [{issue_id: "FOO-43", connection_error: "Oops"}] ) });
    expect(screen.queryAllByText(/Connection error/).length).toBe(1);
    expect(screen.queryAllByText(/Oops/).length).toBe(1);
});

it('shows a parse error', async () => {
    await act(async () => { renderMetricDebtParameters("count", [], {}, [], [{issue_id: "FOO-43", parse_error: "Oops"}] ) });
    expect(screen.queryAllByText(/Parse error/).length).toBe(1);
    expect(screen.queryAllByText(/Oops/).length).toBe(1);
});

it('creates an issue', async () => {
    window.open = jest.fn()
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true, error: "", issue_url: "https://tracker/foo-42" });
    await act(async () => { renderMetricDebtParameters("count", [], reportWithIssueTracker) });
    fireEvent.click(screen.getByText(/Create new issue/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/issue/new", { metric_url: "http://localhost/#metric_uuid" });
});

it('tries to create an issue', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: false, error: "Dummy", issue_url: "" });
    await act(async () => { renderMetricDebtParameters("count", [], reportWithIssueTracker) });
    fireEvent.click(screen.getByText(/Create new issue/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/issue/new", { metric_url: "http://localhost/#metric_uuid" });
});

it('does not show the create issue button if the user has no permissions', async () => {
    await act(async () => { renderMetricDebtParameters("count", [], reportWithIssueTracker, []) });
    expect(screen.queryAllByText(/Create new issue/).length).toBe(0)
})

it('adds an issue id', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] });
    await act(async () => { renderMetricDebtParameters() });
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), 'FOO-42{Enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/issue_ids", { issue_ids: ["FOO-42"] });
});

it('shows issue id suggestions', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] });
    await act(async () => { renderMetricDebtParameters("count", [], { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } }) });
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), 'u');
    await waitFor(() => {
        expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(1);
    })
});

it('shows no issue id suggestions without a query', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] });
    await act(async () => { renderMetricDebtParameters("count", [], { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } }) });
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), 's');
    await waitFor(() => {
        expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(1);
    })
    await userEvent.clear(screen.getByLabelText(/Issue identifiers/).firstChild);
    await waitFor(() => {
        expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(0);
    })
});

it('adds a comment', async () => {
    await act(async () => { renderMetricDebtParameters() });
    await userEvent.type(screen.getByLabelText(/Comment/), 'Keep cool{Tab}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/comment", { comment: "Keep cool" });
});
