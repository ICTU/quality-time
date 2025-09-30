import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { MetricConfigurationParameters } from "./MetricConfigurationParameters"

const dataModel = {
    scales: {
        count: { name: "Count" },
        percentage: { name: "Percentage" },
        version_number: { name: "Version number" },
    },
    subjects: {
        subject_type: {
            metrics: ["violations", "source_version"],
        },
    },
    metrics: {
        violations: {
            unit: "violations",
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count", "percentage"],
        },
        source_version: {
            unit: "",
            direction: "<",
            name: "Source version",
            default_scale: "version_number",
            scales: ["version_number"],
        },
    },
}

beforeEach(() => vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true }))

afterEach(() => vi.clearAllMocks())

async function renderMetricParameters(scale = "count") {
    let result
    await act(async () => {
        result = render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <DataModel.Provider value={dataModel}>
                    <MetricConfigurationParameters
                        subject={{ type: "subject_type" }}
                        metric={{
                            type: "violations",
                            scale: scale,
                        }}
                        metricUuid="metric_uuid"
                        reload={vi.fn()}
                        report={{ subjects: {} }}
                    />
                </DataModel.Provider>
            </Permissions.Provider>,
        )
    })
    return result
}

async function typeInField(label, text, confirm = "Enter") {
    await userEvent.type(screen.getByLabelText(label), `${text}{${confirm}}`, {
        initialSelectionStart: 0,
        initialSelectionEnd: 11,
    })
}

function expectMetricAttributePost(attribute, payload) {
    const endPoint = `metric/metric_uuid/attribute/${attribute}`
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", endPoint, { [attribute]: payload })
}

it("sets the metric name", async () => {
    const { container } = await renderMetricParameters()
    await typeInField(/Metric name/, "New metric name")
    expectMetricAttributePost("name", "New metric name")
    await expectNoAccessibilityViolations(container)
})

it("sets the metric secondary name", async () => {
    const { container } = await renderMetricParameters()
    await typeInField(/Metric secondary name/, "New metric secondary name")
    expectMetricAttributePost("secondary_name", "New metric secondary name")
    await expectNoAccessibilityViolations(container)
})

it("adds a tag on enter", async () => {
    const { container } = await renderMetricParameters()
    await typeInField(/Metric tags/, "New tag", "Enter")
    expectMetricAttributePost("tags", ["New tag"])
    await expectNoAccessibilityViolations(container)
})

it("adds a tag on tab", async () => {
    const { container } = await renderMetricParameters()
    await typeInField(/Metric tags/, "New tag", "Tab")
    expectMetricAttributePost("tags", ["New tag"])
    await expectNoAccessibilityViolations(container)
})

it("changes the scale", async () => {
    const { container } = await renderMetricParameters()
    fireEvent.mouseDown(screen.getByLabelText(/Metric scale/))
    fireEvent.click(screen.getByText(/Percentage/))
    expectMetricAttributePost("scale", "percentage")
    await expectNoAccessibilityViolations(container)
})

it("changes the direction", async () => {
    const { container } = await renderMetricParameters()
    fireEvent.mouseDown(screen.getByLabelText(/direction/))
    fireEvent.click(screen.getByText(/More violations is better/))
    expectMetricAttributePost("direction", ">")
    await expectNoAccessibilityViolations(container)
})

it("sets the metric unit for metrics with the count scale", async () => {
    const { container } = await renderMetricParameters()
    await typeInField(/Metric unit/, "New metric unit")
    expectMetricAttributePost("unit", "New metric unit")
    await expectNoAccessibilityViolations(container)
})

it("sets the metric unit field for metrics with the percentage scale", async () => {
    const { container } = await renderMetricParameters("percentage")
    await typeInField(/Metric unit/, "New metric unit")
    expectMetricAttributePost("unit", "New metric unit")
    await expectNoAccessibilityViolations(container)
})

it("skips the metric unit field for metrics with the version number scale", async () => {
    const { container } = render(
        <DataModel.Provider value={dataModel}>
            <MetricConfigurationParameters
                report={{ subjects: {} }}
                subject={{ type: "subject_type" }}
                metric={{ type: "source_version" }}
                metricUuid="metric_uuid"
            />
        </DataModel.Provider>,
    )
    expect(screen.queryAllByText(/Metric unit/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("turns off evaluation of targets", async () => {
    const { container } = await renderMetricParameters()
    await userEvent.type(screen.getByLabelText(/Evaluate metric targets/), "No{Enter}")
    expectMetricAttributePost("evaluate_targets", false)
    await expectNoAccessibilityViolations(container)
})
