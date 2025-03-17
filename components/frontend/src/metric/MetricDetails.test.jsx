import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { act, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as changelog_api from "../api/changelog"
import * as fetch_server_api from "../api/fetch_server_api"
import * as measurement_api from "../api/measurement"
import * as source_api from "../api/source"
import { DataModel } from "../context/DataModel"
import { EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import * as toast from "../widgets/toast"
import { MetricDetails } from "./MetricDetails"

vi.mock("../api/fetch_server_api.js")
vi.mock("../api/changelog.js")
vi.mock("../api/measurement.js")
vi.mock("../api/source.js")
vi.mock("../widgets/toast.jsx")

beforeEach(() => {
    history.push("")
    fetch_server_api.fetch_server_api.mockImplementation(() => Promise.resolve())
})

afterEach(() => vi.restoreAllMocks())

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

function getMetricMeasurementsSuccessfully(connection_error) {
    return Promise.resolve({
        ok: true,
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

async function renderMetricDetails({
    stopFilteringAndSorting = null,
    connection_error = null,
    getMetricMeasurements = null,
} = {}) {
    measurement_api.get_metric_measurements.mockImplementation(() => {
        return getMetricMeasurements ? getMetricMeasurements() : getMetricMeasurementsSuccessfully(connection_error)
    })
    source_api.set_source_entity_attribute.mockImplementation(
        (_metric_uuid, _source_uuid, _entity_key, _attribute, _value, reload) => reload(),
    )
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }))
    let result
    const settings = createTestableSettings()
    await act(async () => {
        result = render(
            <LocalizationProvider dateAdapter={AdapterDayjs}>
                <Permissions.Provider value={[EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION]}>
                    <DataModel.Provider value={dataModel}>
                        <MetricDetails
                            metric_uuid="metric_uuid"
                            reload={vi.fn()}
                            report={report}
                            reports={[report]}
                            settings={settings}
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
        clipboard: { writeText: vi.fn().mockImplementation(() => Promise.resolve()) },
    })
    await renderMetricDetails()
    await act(async () => {
        fireEvent.click(screen.getByText(/Share/))
    })
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("http://localhost:3000/#metric_uuid")
})

it("displays whether sources have errors", async () => {
    const { container } = await renderMetricDetails({ connection_error: "Connection error" })
    expect(screen.getByText(/Sources/)).toHaveClass("error")
    await expectNoAccessibilityViolations(container)
})

it("displays whether sources have warnings", async () => {
    const { container } = await renderMetricDetails()
    expect(screen.getByText(/Sources/)).toHaveClass("warning")
    await expectNoAccessibilityViolations(container)
})

it("moves the metric", async () => {
    const mockCallback = vi.fn()
    await renderMetricDetails({ stopFilteringAndSorting: mockCallback })
    await act(async () => fireEvent.click(screen.getByRole("button", { name: /Move metric to the last row/ })))
    expect(mockCallback).toHaveBeenCalled()
    expect(measurement_api.get_metric_measurements).toHaveBeenCalled()
})

it("deletes the metric", async () => {
    history.push("?expanded=metric_uuid:1")
    await renderMetricDetails()
    fireEvent.click(screen.getByText(/Delete metric/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("delete", "metric/metric_uuid", {})
    expect(history.location.search).toEqual("")
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

it("does not measure the metric if the metric source configuration is incomplete", async () => {
    dataModel.sources["sonarqube"].parameters = { url: { mandatory: true, metrics: ["violations"] } }
    await renderMetricDetails()
    fireEvent.click(screen.getByText(/Measure metric/))
    expect(fetch_server_api.fetch_server_api).not.toHaveBeenCalled()
})

it("fails to load measurements due to a failed promise", async () => {
    history.push("?expanded=metric_uuid:5")
    const { container } = await renderMetricDetails({
        getMetricMeasurements: () => Promise.reject(new Error("Failure")),
    })
    expect(screen.queryAllByText(/Loading measurements failed/).length).toBe(1)
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not fetch measurements", "Failure")
    await expectNoAccessibilityViolations(container)
})

it("fails to load measurements due to an internal server error", async () => {
    history.push("?expanded=metric_uuid:5")
    const { container } = await renderMetricDetails({
        getMetricMeasurements: () => Promise.resolve({ ok: false, statusText: "Internal Server Error" }),
    })
    expect(screen.queryAllByText(/Loading measurements failed/).length).toBe(1)
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not fetch measurements", "Internal Server Error")
    await expectNoAccessibilityViolations(container)
})

it("reloads the measurements after editing a measurement entity", async () => {
    history.push("?expanded=metric_uuid:5")
    const { container } = await renderMetricDetails()
    expect(measurement_api.get_metric_measurements).toHaveBeenCalledTimes(1)
    fireEvent.click(screen.getByRole("button", { name: "Expand/collapse" }))
    await expectNoAccessibilityViolations(container)
    fireEvent.mouseDown(screen.getByText("Unconfirm"))
    await act(async () => fireEvent.click(screen.getByText("Confirm")))
    expect(measurement_api.get_metric_measurements).toHaveBeenCalledTimes(2)
})
