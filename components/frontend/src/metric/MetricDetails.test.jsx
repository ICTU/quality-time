import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { act, fireEvent, render, screen } from "@testing-library/react"
import { locale_en_gb } from "dayjs/locale/en-gb"
import history from "history/browser"

import * as changelog_api from "../api/changelog"
import * as fetch_server_api from "../api/fetch_server_api"
import * as measurement_api from "../api/measurement"
import * as source_api from "../api/source"
import { DataModel } from "../context/DataModel"
import { EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { MetricDetails } from "./MetricDetails"

jest.mock("../api/fetch_server_api")
jest.mock("../api/changelog.js")
jest.mock("../api/measurement.js")
jest.mock("../api/source.js")

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
                            type: "sonarqube",
                            entities: [],
                        },
                    },
                },
                metric_uuid2: { name: "Metric 2", sources: {} },
            },
        },
    },
}

const dataModel = {
    sources: {
        sonarqube: {
            name: "The source",
            deprecated: true,
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
    metrics: {
        violations: {
            direction: "<",
            tags: [],
            sources: ["sonarqube"],
            scales: ["count", "percentage", "version_number"],
        },
    },
    subjects: { subject_type: { metrics: ["violations"] } },
}

async function renderMetricDetails(stopFilteringAndSorting, connection_error, failLoadingMeasurements) {
    measurement_api.get_metric_measurements.mockImplementation(() => {
        if (failLoadingMeasurements) {
            return Promise.reject(new Error("failed to load measurements"))
        } else {
            return Promise.resolve({
                measurements: [
                    {
                        count: { value: "42" },
                        version_number: { value: "1.1" },
                        start: "2020-02-29T10:25:52.252Z",
                        end: "2020-02-29T11:25:52.252Z",
                        sources: [
                            {},
                            { source_uuid: "source_uuid2" },
                            {
                                source_uuid: "source_uuid",
                                entities: [{ key: "1" }],
                                connection_error: connection_error,
                            },
                        ],
                    },
                ],
            })
        }
    })
    source_api.set_source_entity_attribute.mockImplementation(
        (_metric_uuid, _source_uuid, _entity_key, _attribute, _value, reload) => reload(),
    )
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }))
    let result
    await act(async () => {
        result = render(
            <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale={locale_en_gb}>
                <Permissions.Provider value={[EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION]}>
                    <DataModel.Provider value={dataModel}>
                        <MetricDetails
                            metric_uuid="metric_uuid"
                            reload={jest.fn()}
                            report={report}
                            reports={[report]}
                            stopFilteringAndSorting={stopFilteringAndSorting}
                            subject_uuid="subject_uuid"
                        />
                    </DataModel.Provider>
                </Permissions.Provider>
            </LocalizationProvider>,
        )
    })
    return result
}

beforeEach(() => {
    jest.clearAllMocks()
    history.push("")
    fetch_server_api.fetch_server_api.mockImplementation(() => Promise.resolve())
})

it("switches tabs", async () => {
    const { container } = await renderMetricDetails()
    expect(screen.getAllByLabelText(/Metric name/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
    fireEvent.click(screen.getByText(/Sources/))
    expect(screen.getAllByLabelText(/Source name/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("switches tabs to technical debt", async () => {
    const { container } = await renderMetricDetails()
    expect(screen.getAllByLabelText(/Metric name/).length).toBe(1)
    fireEvent.click(screen.getByText(/Technical debt/))
    expect(screen.getAllByLabelText(/Metric technical debt target/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("switches tabs to measurement entities", async () => {
    const { container } = await renderMetricDetails()
    expect(screen.getAllByLabelText(/Metric name/).length).toBe(1)
    fireEvent.click(screen.getByText(/The source/))
    expect(screen.getAllByText(/Attribute status/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("switches tabs to the trend graph", async () => {
    const { container } = await renderMetricDetails()
    expect(screen.getAllByLabelText(/Metric name/).length).toBe(1)
    fireEvent.click(screen.getByText(/Trend graph/))
    expect(screen.getAllByText(/Time/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the trend graph tab even if the metric scale is version number", async () => {
    report.subjects["subject_uuid"].metrics["metric_uuid"].scale = "version_number"
    const { container } = await renderMetricDetails()
    expect(screen.queryAllByText(/Trend graph/).length).toBe(1)
    report.subjects["subject_uuid"].metrics["metric_uuid"].scale = "count"
    await expectNoAccessibilityViolations(container)
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
    const { container } = await renderMetricDetails(null, "Connection error")
    expect(screen.getByText(/Sources/)).toHaveClass("error")
    await expectNoAccessibilityViolations(container)
})

it("displays whether sources have warnings", async () => {
    const { container } = await renderMetricDetails()
    expect(screen.getByText(/Sources/)).toHaveClass("warning")
    await expectNoAccessibilityViolations(container)
})

it("moves the metric", async () => {
    const mockCallback = jest.fn()
    await renderMetricDetails(mockCallback)
    await act(async () => fireEvent.click(screen.getByRole("button", { name: /Move metric to the last row/ })))
    expect(mockCallback).toHaveBeenCalled()
    expect(measurement_api.get_metric_measurements).toHaveBeenCalled()
})

it("loads the changelog", async () => {
    const { container } = await renderMetricDetails()
    await act(async () => fireEvent.click(screen.getByText(/Changelog/)))
    expect(changelog_api.get_changelog).toHaveBeenCalledWith(5, { metric_uuid: "metric_uuid" })
    await expectNoAccessibilityViolations(container)
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

it("fails to load measurements", async () => {
    const { container } = await renderMetricDetails(null, null, true)
    fireEvent.click(screen.getByText(/Trend graph/))
    expect(screen.queryAllByText(/Loading measurements failed/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("reloads the measurements after editing a measurement entity", async () => {
    const { container } = await renderMetricDetails()
    expect(measurement_api.get_metric_measurements).toHaveBeenCalledTimes(1)
    fireEvent.click(screen.getByText(/The source/))
    fireEvent.click(screen.getByRole("button", { name: "Expand/collapse" }))
    await expectNoAccessibilityViolations(container)
    fireEvent.mouseDown(screen.getByText("Unconfirm"))
    await act(async () => fireEvent.click(screen.getByText("Confirm")))
    expect(measurement_api.get_metric_measurements).toHaveBeenCalledTimes(2)
})
