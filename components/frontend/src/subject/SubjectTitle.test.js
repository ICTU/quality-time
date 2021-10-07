import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { SubjectTitle } from './SubjectTitle';
import * as fetch_server_api from '../api/fetch_server_api';
import { DataModel } from '../context/Contexts';

const datamodel = {
    subjects: {
        subject_type: { name: "Default subject type" },
        subject_type2: { name: "Other subject type" }
    }, metrics: {
        metric_type: { tags: [] },
    }
}
const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            type: "subject_type", name: "Subject title", metrics: { metric_uuid: { type: "metric_type", tags: [] } }
        }
    }
};

async function render_subject_title(subject_type = "subject_type") {
    await act(async () => {
        render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <DataModel.Provider value={datamodel}>
                    <SubjectTitle report={report} subject={{ type: subject_type }} subject_uuid="subject_uuid" />
                </DataModel.Provider>
            </Permissions.Provider>
        )
        fireEvent.click(screen.getByTitle(/expand/));
    });
}

it('changes the subject type', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await render_subject_title();
    userEvent.click(screen.getAllByText(/Default subject type/)[1]);
    userEvent.click(screen.getByText(/Other subject type/));
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/subject_uuid/attribute/type", { type: "subject_type2" });
});

it('deals with unknown subject types', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await render_subject_title("unknown_subject_type");
    expect(screen.getAllByText("Unknown subject type").length).toBe(2);
});

it('changes the subject name', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await render_subject_title();
    userEvent.type(screen.getByLabelText(/Subject name/), '{selectall}{del}New name{enter}');
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/subject_uuid/attribute/name", { name: "New name" });
});

it('loads the changelog', async () => {
    await render_subject_title();
    await act(async () => {
        fireEvent.click(screen.getByText(/Changelog/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/subject/subject_uuid/5");
});

it('moves the subject', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await render_subject_title();
    await act(async () => {
        fireEvent.click(screen.getByLabelText(/Move subject to the next position/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/subject_uuid/attribute/position", { position: "next" });
});

it('deletes the subject', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    await render_subject_title();
    await act(async () => {
        fireEvent.click(screen.getByText(/Delete subject/));
    });
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("delete", "subject/subject_uuid", {});
});
