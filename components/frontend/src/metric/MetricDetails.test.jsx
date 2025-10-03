import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { act, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import * as measurementApi from "../api/measurement"
import { DataModel } from "../context/DataModel"
import { EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import {
    asyncClickButton,
    asyncClickText,
    clickButton,
    clickText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectNoFetch,
    expectNoText,
    expectSearch,
    expectText,
} from "../testUtils"
import * as toast from "../widgets/toast"
import { MetricDetails } from "./MetricDetails"

beforeEach(() => {
    history.push("")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() => Promise.resolve({ changelog: [] }))
    vi.spyOn(toast, "showMessage")
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

function getMetricMeasurementsSuccessfully(connectionError) {
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
                        connection_error: connectionError,
                    },
                ],
            },
        ],
    })
}

async function renderMetricDetails({
    stopFilteringAndSorting = null,
    connectionError = null,
    getMetricMeasurements = null,
} = {}) {
    vi.spyOn(measurementApi, "getMetricMeasurements").mockImplementation(() => {
        return getMetricMeasurements ? getMetricMeasurements() : getMetricMeasurementsSuccessfully(connectionError)
    })
    let result
    const settings = createTestableSettings()
    await act(async () => {
        result = render(
            <LocalizationProvider dateAdapter={AdapterDayjs}>
                <Permissions.Provider value={[EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION]}>
                    <DataModel.Provider value={dataModel}>
                        <MetricDetails
                            metricUuid="metric_uuid"
                            reload={vi.fn()}
                            report={report}
                            reports={[report]}
                            settings={settings}
                            stopFilteringAndSorting={stopFilteringAndSorting}
                            subjectUuid="subject_uuid"
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
    expectText(/Trend graph/)
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
    await asyncClickText(/Share/)
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("http://localhost:3000/#metric_uuid")
})

it("displays whether sources have errors", async () => {
    const { container } = await renderMetricDetails({ connectionError: "Connection error" })
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
    await asyncClickButton(/Move metric to the last row/)
    expect(mockCallback).toHaveBeenCalled()
    expect(measurementApi.getMetricMeasurements).toHaveBeenCalled()
})

it("deletes the metric", async () => {
    history.push("?expanded=metric_uuid:1")
    await renderMetricDetails()
    clickText(/Delete metric/)
    expectFetch("delete", "metric/metric_uuid", {})
    expectSearch("")
})

it("measures the metric", async () => {
    await renderMetricDetails()
    clickText(/Measure metric/)
    expectFetch(
        "post",
        "metric/metric_uuid/attribute/measurement_requested",
        expect.objectContaining({}), // Ignore the attribute value, it's new Date().toISOString()
    )
})

it("does not measure the metric if the metric source configuration is incomplete", async () => {
    dataModel.sources["sonarqube"].parameters = { url: { mandatory: true, metrics: ["violations"] } }
    await renderMetricDetails()
    clickText(/Measure metric/)
    expectNoFetch()
})

it("loads an empty list of measurements", async () => {
    history.push("?expanded=metric_uuid:5")
    const { container } = await renderMetricDetails({
        getMetricMeasurements: () => Promise.resolve({ measurements: [] }),
    })
    expectNoText(/Loading measurements failed/)
    expect(toast.showMessage).toHaveBeenCalledTimes(0)
    await expectNoAccessibilityViolations(container)
})

it("loads a missing list of measurements", async () => {
    history.push("?expanded=metric_uuid:5")
    const { container } = await renderMetricDetails({
        getMetricMeasurements: () => Promise.resolve({}),
    })
    expectNoText(/Loading measurements failed/)
    expect(toast.showMessage).toHaveBeenCalledTimes(0)
    await expectNoAccessibilityViolations(container)
})

it("fails to load measurements due to a failed promise", async () => {
    history.push("?expanded=metric_uuid:5")
    const { container } = await renderMetricDetails({
        getMetricMeasurements: () => Promise.reject(new Error("Failure")),
    })
    expectText(/Loading measurements failed/)
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not fetch measurements", "Failure")
    await expectNoAccessibilityViolations(container)
})

it("fails to load measurements due to an internal server error", async () => {
    history.push("?expanded=metric_uuid:5")
    const { container } = await renderMetricDetails({
        getMetricMeasurements: () => Promise.resolve({ ok: false, statusText: "Internal Server Error" }),
    })
    expectText(/Loading measurements failed/)
    expect(toast.showMessage).toHaveBeenCalledTimes(1)
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not fetch measurements", "Internal Server Error")
    await expectNoAccessibilityViolations(container)
})

it("reloads the measurements after editing a measurement entity", async () => {
    history.push("?expanded=metric_uuid:5")
    const { container } = await renderMetricDetails()
    expect(measurementApi.getMetricMeasurements).toHaveBeenCalledTimes(1)
    clickButton("Expand/collapse")
    await expectNoAccessibilityViolations(container)
    fireEvent.mouseDown(screen.getByText("Unconfirm"))
    await asyncClickText("Confirm")
    expect(measurementApi.getMetricMeasurements).toHaveBeenCalledTimes(2)
})

it("loads the changelog", async () => {
    history.push("?expanded=metric_uuid:3")
    const { container } = await renderMetricDetails()
    expectFetch("get", "changelog/metric/metric_uuid/5")
    await expectNoAccessibilityViolations(container)
})
