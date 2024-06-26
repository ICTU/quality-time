import { act, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as changelog_api from "../api/changelog"
import * as fetch_server_api from "../api/fetch_server_api"
import * as measurement_api from "../api/measurement"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MetricDetails } from "./MetricDetails"

jest.mock("../api/fetch_server_api")
jest.mock("../api/changelog.js")
jest.mock("../api/measurement.js")

const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            name: "Metric",
            type: "subject_type",
            metrics: {
                metric_uuid: {
                    accept_debt: false,
                    tags: [],
                    type: "violations",
                    sources: {
                        source_uuid: {
                            type: "source_type",
                            entities: [],
                        },
                    },
                },
                metric_uuid2: {},
            },
        },
    },
}

const dataModel = {
    sources: {
        source_type: {
            name: "The source",
            parameters: {},
            parameter_layout: {
                all: {
                    name: "All parameters",
                    parameters: [],
                },
            },
            entities: { violations: { name: "Attribute", attributes: [] } },
        },
    },
    metrics: { violations: { direction: "<", tags: [], sources: ["source_type"] } },
    subjects: { subject_type: { metrics: ["violations"] } },
}

async function renderMetricDetails(stopFilteringAndSorting, connection_error) {
    measurement_api.get_metric_measurements.mockImplementation(() =>
        Promise.resolve({
            ok: true,
            measurements: [
                {
                    count: { value: "42" },
                    version_number: { value: "1.1" },
                    start: "2020-02-29T10:25:52.252Z",
                    end: "2020-02-29T11:25:52.252Z",
                    sources: [
                        {},
                        { source_uuid: "source_uuid" },
                        {
                            source_uuid: "source_uuid",
                            entities: [{ key: "1" }],
                            connection_error: connection_error,
                        },
                    ],
                },
            ],
        }),
    )
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }))
    const settings = createTestableSettings()
    await act(async () =>
        render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <DataModel.Provider value={dataModel}>
                    <MetricDetails
                        metric_uuid="metric_uuid"
                        report={report}
                        reports={[report]}
                        stopFilteringAndSorting={stopFilteringAndSorting}
                        subject_uuid="subject_uuid"
                        expandedItems={settings.expandedItems}
                    />
                </DataModel.Provider>
            </Permissions.Provider>,
        ),
    )
}

beforeEach(() => {
    history.push("")
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({
        then: jest.fn().mockReturnValue({
            catch: jest.fn().mockReturnValue({ finally: jest.fn() }),
        }),
    })
})

it("switches tabs", async () => {
    await renderMetricDetails()
    expect(screen.getAllByText(/Metric name/).length).toBe(1)
    fireEvent.click(screen.getByText(/Sources/))
    expect(screen.getAllByText(/Source name/).length).toBe(1)
})

it("switches tabs to technical debt", async () => {
    await renderMetricDetails()
    expect(screen.getAllByText(/Metric name/).length).toBe(1)
    fireEvent.click(screen.getByText(/Technical debt/))
    expect(screen.getAllByText(/Technical debt target/).length).toBe(1)
})

it("switches tabs to measurement entities", async () => {
    await renderMetricDetails()
    expect(screen.getAllByText(/Metric name/).length).toBe(1)
    fireEvent.click(screen.getByText(/The source/))
    expect(screen.getAllByText(/Attribute status/).length).toBe(1)
})

it("switches tabs to the trend graph", async () => {
    await renderMetricDetails()
    expect(screen.getAllByText(/Metric name/).length).toBe(1)
    fireEvent.click(screen.getByText(/Trend graph/))
    expect(screen.getAllByText(/Time/).length).toBe(1)
})

it("does not show the trend graph tab if the metric scale is version number", async () => {
    report.subjects["subject_uuid"].metrics["metric_uuid"].scale = "version_number"
    await renderMetricDetails()
    expect(screen.queryAllByText(/Trend graph/).length).toBe(0)
})

it("removes the existing hashtag from the URL to share", async () => {
    history.push("#hash_that_should_be_removed")
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: { writeText: jest.fn().mockImplementation(() => Promise.resolve()) },
    })
    await renderMetricDetails()
    await act(async () => {
        fireEvent.click(screen.getByText(/Share/))
    })
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("http://localhost/#metric_uuid")
})

it("displays whether sources have errors", async () => {
    await renderMetricDetails(null, "Connection error")
    expect(screen.getByText(/Sources/)).toHaveClass("red label")
})

it("moves the metric", async () => {
    const mockCallback = jest.fn()
    await renderMetricDetails(mockCallback)
    await act(async () => fireEvent.click(screen.getByLabelText(/Move metric to the last row/)))
    expect(mockCallback).toHaveBeenCalled()
    expect(measurement_api.get_metric_measurements).toHaveBeenCalled()
})

it("loads the changelog", async () => {
    await renderMetricDetails()
    await act(async () => fireEvent.click(screen.getByText(/Changelog/)))
    expect(changelog_api.get_changelog).toHaveBeenCalledWith(5, { metric_uuid: "metric_uuid" })
})

it("deletes the metric", async () => {
    await renderMetricDetails()
    fireEvent.click(screen.getByText(/Delete metric/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("delete", "metric/metric_uuid", {})
})

it("measures the metric", async () => {
    await renderMetricDetails()
    fireEvent.click(screen.getByText(/Measure metric/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith(
        "post",
        "metric/metric_uuid/attribute/measurement_requested",
        expect.objectContaining({}), // Ignore the attribute value, it's new Date().toISOString()
    )
})
