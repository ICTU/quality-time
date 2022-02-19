import React from 'react';
import { act, fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { ReportTitle } from './ReportTitle';
import * as fetch_server_api from '../api/fetch_server_api';

jest.mock("../api/fetch_server_api.js")

function render_report_title() {
    render(
        <DataModel.Provider value={{ sources: { jira: { name: "Jira", issue_tracker: true } } }}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <ReportTitle
                    history={{ location: {} }}
                    report={{ report_uuid: "report_uuid", title: "Report" }}
                />
            </Permissions.Provider>
        </DataModel.Provider>
    )
}

it('deletes the report', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Delete report/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("delete", "report/report_uuid", {});
});

it('sets the title', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Report title/), '{selectall}{del}New title{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/attribute/title", { title: "New title" });
});

it('sets the subtitle', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Report subtitle/), '{selectall}{del}New subtitle{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/attribute/subtitle", { subtitle: "New subtitle" });
});

it('sets the comment', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    userEvent.type(screen.getByLabelText(/Comment/), '{selectall}{del}New comment{shift}{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/attribute/comment", { comment: "New comment" });
});

it('sets the issue tracker type', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker type/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Jira/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/type", { type: "jira" });
});

it('sets the issue tracker url', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker/));
    });
    userEvent.type(screen.getByText(/URL/), '{selectall}{del}https://jira{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/url", { url: "https://jira" });
});

it('sets the issue tracker username', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker/));
    });
    userEvent.type(screen.getByText(/Username/), '{selectall}{del}janedoe{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/username", { username: "janedoe" });
});

it('sets the issue tracker username', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker/));
    });
    userEvent.type(screen.getByText(/Password/), '{selectall}{del}secret{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/password", { password: "secret" });
});

it('sets the issue summary visibility', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker/));
    });
    await act(async () => {
        const dropdown = document.getElementById("issue-summary")
        fireEvent.click(within(dropdown).getByText(/Yes/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/show_issue_summary", { show_issue_summary: true });
});

it('sets the issue creation date visibility', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker/));
    });
    await act(async () => {
        const dropdown = document.getElementById("issue-creation-date")
        fireEvent.click(within(dropdown).getByText(/Yes/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/show_issue_creation_date", { show_issue_creation_date: true });
});

it('sets the issue update date visibility', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Issue tracker/));
    });
    await act(async () => {
        const dropdown = document.getElementById("issue-update-date")
        fireEvent.click(within(dropdown).getByText(/Yes/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "report/report_uuid/issue_tracker/show_issue_update_date", { show_issue_update_date: true });
});

it('loads the changelog', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    await act(async () => {
        fireEvent.click(screen.getByText(/Changelog/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/report/report_uuid/5");
});

it('shows the share tab', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    fireEvent.click(screen.getByText(/Share/));
    expect(screen.getAllByText(/Report permanent link/).length).toBe(1);
})

it('shows the notification destinations', async () => {
    await act(async () => {
        render_report_title();
        fireEvent.click(screen.getByTitle(/expand/));
    });
    fireEvent.click(screen.getByText(/Notifications/));
    expect(screen.getAllByText(/No notification destinations/).length).toBe(2);
});