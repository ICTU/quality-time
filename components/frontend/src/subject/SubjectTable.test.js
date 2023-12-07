import React from 'react';
import { act, fireEvent, render, renderHook, screen } from '@testing-library/react';
import history from 'history/browser';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions";
import { useVisibleDetailsTabsSearchQuery } from '../app_ui_settings';
import * as fetch_server_api from '../api/fetch_server_api';
import { createTestableSettings } from '../__fixtures__/fixtures';
import { SubjectTable } from './SubjectTable';

jest.mock("../api/fetch_server_api.js")
fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: false });

const metric = {
    unit: "testUnit",
    scale: "count",
    type: "metric_type",
    name: "name_1",
    sources: {},
    tags: ["Tag 1"]
}
const metric2 = {
    unit: "tests",
    scale: "percentage",
    name: "name_2",
    type: "metric_type",
}
const datamodel = {
    metrics: {
        metric_type: { name: "Metric type", sources: ["source_type"], tags: [] }
    },
    sources: {
        source_type: { name: "Source type"}
    },
    subjects: {
        subject_type: { metrics: ["metric_type"] }
    }
}

const dates = [
    new Date("2020-01-15T00:00:00+00:00"),
    new Date("2020-01-14T00:00:00+00:00"),
    new Date("2020-01-13T00:00:00+00:00"),
]

function renderSubjectTable(
    {
        dates = [],
        visibleDetailsTabs = null
    } = {}
) {
    let settings = createTestableSettings()
    if (visibleDetailsTabs) { settings.visibleDetailsTabs = visibleDetailsTabs }
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={datamodel}>
                <SubjectTable
                    dates={dates}
                    handleSort={jest.fn()}
                    reportDate={new Date("2020-01-15T00:00:00+00:00")}
                    report={{ report_uuid: "report_uuid", subjects: { subject_uuid: { type: "subject_type", metrics: { 1: metric, 2: metric2 } } } }}
                    measurements={
                        [
                            { metric_uuid: "1", start: "2020-01-14T00:00:00+00:00", end: "2020-01-15T00:00:00+00:00", count: { status: "target_met" } },
                            { metric_uuid: "1", start: "2020-01-15T00:00:00+00:00", end: "2020-01-16T00:00:00+00:00", count: { status: "target_met" } },
                            { metric_uuid: "1", start: "2020-01-16T00:00:00+00:00", end: "2020-01-17T00:00:00+00:00", count: { status: "target_not_met" } },
                            { metric_uuid: "2", start: "2020-01-10T00:00:00+00:00", end: "2020-01-10T00:00:00+00:00", count: { status: "target_not_met" } },
                            { metric_uuid: "3", start: "2020-01-14T00:00:00+00:00", end: "2020-01-15T00:00:00+00:00", count: { status: "target_not_met" } },
                        ]
                    }
                    metricEntries={Object.entries({ 1: metric, 2: metric2 })}
                    settings={settings}
                    subject={{ type: "subject_type", metrics: { 1: metric, 2: metric2 } }}
                    subject_uuid="subject_uuid"
                />
            </DataModel.Provider>
        </Permissions.Provider>
    );
}

beforeEach(() => {
    history.push("")
})

it('displays all the metrics', () => {
    renderSubjectTable()
    const metricNames = ["name_1", "name_2"]
    metricNames.forEach(metricName => {
        expect(screen.queryAllByText(metricName).length).toBe(1)
    })
});

it('shows the date columns', () => {
    renderSubjectTable({ dates: dates })
    dates.forEach((date) => {
        expect(screen.queryAllByText(date.toLocaleDateString()).length).toBe(1)
    })
})

it('shows the source column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Source/).length).toBe(1)
})

it('hides the source column', () => {
    history.push("?hidden_columns=source")
    renderSubjectTable()
    expect(screen.queryAllByText(/Source/).length).toBe(0)
})

it('shows the time left column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Time left/).length).toBe(1)
})

it('hides the time left column', () => {
    history.push("?hidden_columns=time_left")
    renderSubjectTable()
    expect(screen.queryAllByText(/Time left/).length).toBe(0)
})

it('does not show the overrun column when showing one date', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/[Oo]verrun/).length).toBe(0)
})

it('shows the overrun column when showing multiple dates', () => {
    renderSubjectTable({ dates: dates })
    expect(screen.queryAllByText(/[Oo]verrun/).length).toBe(1)
})

it('hides the overrun column when showing multiple dates', () => {
    history.push("?hidden_columns=overrun")
    renderSubjectTable()
    expect(screen.queryAllByText(/[Oo]verrun/).length).toBe(0)
})

it('shows the comment column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Comment/).length).toBe(1)
})

it('hides the source column', () => {
    history.push("?hidden_columns=comment")
    renderSubjectTable()
    expect(screen.queryAllByText(/Comment/).length).toBe(0)
})

it('shows the issue column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Issues/).length).toBe(1)
})

it('hides the issue column', () => {
    history.push("?hidden_columns=issues")
    renderSubjectTable()
    expect(screen.queryAllByText(/Issues/).length).toBe(0)
})

it('shows the tags column', () => {
    renderSubjectTable()
    expect(screen.queryAllByText(/Tags/).length).toBe(1)
    expect(screen.queryAllByText(/Tag 1/).length).toBe(1)
})

it('hides the tags column', () => {
    history.push("?hidden_columns=tags")
    renderSubjectTable()
    expect(screen.queryAllByText(/Tags/).length).toBe(0)
    expect(screen.queryAllByText(/Tag 1/).length).toBe(0)
})

it('expands the details via the button', () => {
    const visibleDetailsTabs = renderHook(() => useVisibleDetailsTabsSearchQuery())
    renderSubjectTable({ visibleDetailsTabs: visibleDetailsTabs.result.current })
    const expand = screen.getAllByRole("button")[0];
    fireEvent.click(expand);
    visibleDetailsTabs.rerender()
    expect(visibleDetailsTabs.result.current.value).toStrictEqual(["1:0"]);
})

it('collapses the details via the button', () => {
    history.push("?tabs=1:0")
    const visibleDetailsTabs = renderHook(() => useVisibleDetailsTabsSearchQuery())
    renderSubjectTable({ visibleDetailsTabs: visibleDetailsTabs.result.current })
    const expand = screen.getAllByRole("button")[0];
    fireEvent.click(expand);
    visibleDetailsTabs.rerender()
    expect(visibleDetailsTabs.result.current.value).toStrictEqual([]);
})

it('expands the details via the url', () => {
    renderSubjectTable()
    expect(screen.queryAllByText("Configuration").length).toBe(0)
    history.push("?tabs=1:0")
    renderSubjectTable()
    expect(screen.queryAllByText("Configuration").length).toBe(1)
})

it('moves a metric', async () => {
    history.push("?tabs=1:2")
    renderSubjectTable()
    await act(async () => fireEvent.click(await screen.findByLabelText("Move metric to the next row")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "metric/1/attribute/position", { position: "next" });
})

it('adds a source', async () => {
    history.push("?tabs=1:2")
    renderSubjectTable()
    const addButton = await screen.findByText("Add source")
    await act(async () => fireEvent.click(addButton))
    fireEvent.click(await screen.findByText("Source type"))
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("post", "source/new/1", { type: "source_type" });
})
