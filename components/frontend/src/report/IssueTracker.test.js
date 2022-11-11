import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import * as report_api from '../api/report';
import { IssueTracker } from './IssueTracker';

jest.mock("../api/report.js")
report_api.get_report_issue_tracker_options.mockImplementation(
    () => Promise.resolve(
        {
            projects: [{ key: "PRJ", name: "Project name" }],
            issue_types: [{ key: "Bug", name: "Bug" }],
            fields: [{key: "labels", name: "Labels"}],
            epic_links: [{key: "FOO-420", name: "FOO-420"}]
        }
    )
)

const reload = () => { /* Dummy implementation */ }

function render_issue_tracker({ report = { report_uuid: "report_uuid", title: "Report" }, help_url = "" } = {}) {
    return render(
        <DataModel.Provider value={
            {
                sources:
                {
                    jira: { name: "Jira", issue_tracker: true, parameters: { private_token: { help_url: help_url } } }
                }
            }
        }>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <IssueTracker
                    report={report}
                    reload={reload}
                />
            </Permissions.Provider>
        </DataModel.Provider>
    )
}

it('sets the issue tracker type', async () => {
    await act(async () => { render_issue_tracker() });
    await act(async () => { fireEvent.click(screen.getByText(/Issue tracker type/)) });
    await act(async () => { fireEvent.click(screen.getByText(/Jira/)) });
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "type", "jira", reload);
});

it('sets the issue tracker url', async () => {
    await act(async () => { render_issue_tracker() });
    await userEvent.type(screen.getByText(/URL/), 'https://jira{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "url", "https://jira", reload);
});

it('sets the issue tracker username', async () => {
    await act(async () => { render_issue_tracker() });
    await userEvent.type(screen.getByText(/Username/), 'janedoe{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "username", "janedoe", reload);
});

it('sets the issue tracker password', async () => {
    await act(async () => { render_issue_tracker() });
    await userEvent.type(screen.getByText(/Password/), 'secret{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "password", "secret", reload);
});

it('sets the issue tracker private token', async () => {
    await act(async () => { render_issue_tracker() });
    await userEvent.type(screen.getByText(/Private token/), 'secret{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "private_token", "secret", reload);
});

it('does not show the issue tracker private token help url if there is no issue tracker', async () => {
    await act(async () => {
        const { container } = render_issue_tracker({ report: { report_uuid: "report_uuid", title: "Report", issue_tracker: {} }, help_url: "https://help" });
        expect(container.querySelector("a")).toBe(null)
    });
});

it('does not show the issue tracker private token help url if the data model has no help url', async () => {
    await act(async () => {
        const { container } = render_issue_tracker({ report_uuid: "report_uuid", title: "Report", issue_tracker: { type: "jira" } });
        expect(container.querySelector("a")).toBe(null)
    });
});

it('shows the issue tracker private token help url', async () => {
    let result;
    await act(async () => { result = render_issue_tracker({ report: { report_uuid: "report_uuid", title: "Report", issue_tracker: { type: "jira" } }, help_url: "https://help" }); });
    expect(result.container.querySelector("a")).toHaveAttribute('href', 'https://help')
});

it('sets the issue tracker project', async () => {
    await act(async () => { render_issue_tracker() });
    await act(async () => { fireEvent.click(screen.getByText(/Project for new issues/)) });
    await act(async () => { fireEvent.click(screen.getByText(/Project name/)) });
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "project_key", "PRJ", reload);
});

it('sets the issue tracker issue type', async () => {
    await act(async () => { render_issue_tracker() });
    await act(async () => { fireEvent.click(screen.getByText(/Issue type/)) });
    await act(async () => { fireEvent.click(screen.getByText(/Bug/)) });
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "issue_type", "Bug", reload);
});

it('sets the issue tracker issue labels', async () => {
    await act(async () => { render_issue_tracker() });
    await userEvent.type(screen.getByText(/Enter one or more labels here/), 'Label{Enter}');
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "issue_labels", ["Label"], reload);
});

it('sets the issue tracker epic link', async () => {
    await act(async () => { render_issue_tracker() });
    await act(async () => { fireEvent.click(screen.getByText(/Epic link/)) });
    await act(async () => { fireEvent.click(screen.getByText(/FOO-420/)) });
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith("report_uuid", "epic_link", "FOO-420", reload);
});

it('does not show the issue labels warning without tracker project', async () => {
    await act(async () => {
        render_issue_tracker(
            { report: { report_uuid: "report_uuid", title: "Report", issue_tracker: { type: "jira" } } }
        )
    });
    expect((screen.queryAllByText(/Labels not supported/)).length).toBe(0)
});

it('does not show the issue labels warning without issue type', async () => {
    await act(async () => {
        render_issue_tracker(
            { report: { report_uuid: "report_uuid", title: "Report", issue_tracker: { type: "jira", parameters: { project_key: "PRJ" } } } }
        )
    });
    expect((screen.queryAllByText(/Labels not supported/)).length).toBe(0)
});

it('does not show the issue labels warning with issue type that supports labels', async () => {
    await act(async () => {
        render_issue_tracker(
            { report: { report_uuid: "report_uuid", title: "Report", issue_tracker: { type: "jira", parameters: { project_key: "PRJ", issue_type: "Bug" } } } }
        )
    });
    expect((screen.queryAllByText(/Labels not supported/)).length).toBe(0)
});

it('does show the issue labels warning with issue type that does not support labels', async () => {
    report_api.get_report_issue_tracker_options.mockImplementation(
        () => Promise.resolve(
            {
                projects: [{ key: "PRJ", name: "Project name" }],
                issue_types: [{ key: "Bug", name: "Bug" }],
                fields: [],
                epic_links: []
            }
        )
    )
    await act(async () => {
        render_issue_tracker(
            { report: { report_uuid: "report_uuid", title: "Report", issue_tracker: { type: "jira", parameters: { project_key: "PRJ", issue_type: "Bug" } } } }
        )
    });
    expect((screen.queryAllByText(/Labels not supported/)).length).toBe(1)
});
