import { render, screen } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import {
    expectNoAccessibilityViolations,
    expectNoText,
    expectNoTextAfterWait,
    expectText,
    expectTextAfterWait,
    hoverText,
} from "../testUtils"
import { MeasurementValue } from "./MeasurementValue"

function renderMeasurementValue({
    latestMeasurement = {},
    measurementRequested = null,
    reportDate = null,
    scale = "count",
    status = null,
    type = "violations",
    unit = null,
    unit_singular = null,
    url = "https://example.org",
} = {}) {
    return render(
        <DataModel.Provider
            value={{
                metrics: { violations: { unit: "violations", unit_singular: "violation" } },
                sources: { source_type: { parameters: { url: { mandatory: true, metrics: ["violations"] } } } },
            }}
        >
            <MeasurementValue
                metric={{
                    latest_measurement: latestMeasurement,
                    measurement_requested: measurementRequested,
                    scale: scale,
                    sources: { source_uuid: { type: "source_type", parameters: { url: url } } },
                    status: status,
                    type: type,
                    unit: unit,
                    unit_singular: unit_singular,
                }}
                reportDate={reportDate}
            />
        </DataModel.Provider>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderMeasurementValue({ latestMeasurement: { count: { value: "42" } } })
    await expectNoAccessibilityViolations(container)
})

it("renders the value", async () => {
    renderMeasurementValue({ latestMeasurement: { count: { value: "42" } } })
    expectText(/42/)
})

it("renders an unknown value", async () => {
    renderMeasurementValue({ latestMeasurement: { count: { value: null } } })
    expectText(/\?/)
    expect(screen.queryAllByTestId("LoopIcon").length).toBe(0)
})

it("renders a value that has not been measured yet", async () => {
    renderMeasurementValue()
    expectText(/\?/)
    expect(screen.queryAllByTestId("LoopIcon").length).toBe(0)
})

it("renders a value that can not be measured yet", async () => {
    renderMeasurementValue({
        latestMeasurement: {
            count: { value: 1 },
            outdated: true,
            start: new Date().toISOString(),
            end: new Date().toISOString(),
        },
        url: "",
    })
    expectText(/1/)
    expect(screen.queryAllByTestId("LoopIcon").length).toBe(0)
})

it("renders an outdated value", async () => {
    renderMeasurementValue({
        latestMeasurement: {
            count: { value: 1 },
            outdated: true,
            start: new Date().toISOString(),
            end: new Date().toISOString(),
        },
    })
    expect(screen.getAllByTestId("LoopIcon").length).toBe(1)
    await hoverText(/1/)
    await expectTextAfterWait(/Latest measurement out of date/)
    expectText(/The source configuration of this metric was changed after the latest measurement/)
})

it("renders a value for which a measurement was requested", async () => {
    const now = new Date().toISOString()
    renderMeasurementValue({
        latestMeasurement: { count: { value: 1 }, start: now, end: now },
        measurementRequested: now,
    })
    expect(screen.getAllByTestId("LoopIcon").length).toBe(1)
    await hoverText(/1/)
    await expectTextAfterWait(/Measurement requested/)
    expectText(/An update of the latest measurement was requested by a user/)
})

it("renders a value for which a measurement was requested, but which is now up to date", async () => {
    const now = new Date().toISOString()
    renderMeasurementValue({
        latestMeasurement: { count: { value: 1 }, start: now, end: now },
        measurementRequested: "2024-01-01T00:00:00",
    })
    expect(screen.queryAllByTestId("LoopIcon").length).toBe(0)
    await hoverText(/1/)
    await expectNoTextAfterWait(/Measurement requested/)
    expectNoText(/An update of the latest measurement was requested by a user/)
})

it("renders a minutes value", async () => {
    renderMeasurementValue({
        type: "duration",
        unit: "foo units",
        latestMeasurement: { count: { value: "42" } },
    })
    expectText(/42/)
})

it("renders an unknown minutes value", async () => {
    renderMeasurementValue({
        type: "duration",
        unit: "foo units",
        latestMeasurement: { count: { value: null } },
    })
    expectText(/\?/)
})

it("renders a minutes percentage", async () => {
    renderMeasurementValue({
        type: "duration",
        scale: "percentage",
        unit: "foo units",
        latestMeasurement: { percentage: { value: "42" } },
    })
    expectText(/42%/)
})

it("renders an unknown minutes percentage", async () => {
    renderMeasurementValue({
        type: "duration",
        scale: "percentage",
        unit: "foo units",
        latestMeasurement: { percentage: { value: null } },
    })
    expectText(/\?%/)
})

it("shows when the metric was last measured", async () => {
    renderMeasurementValue({
        status: "target_met",
        latestMeasurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00", count: { value: "42" } },
    })
    await hoverText(/42/)
    await expectTextAfterWait(/The metric was last measured/)
})

it("shows when the last measurement attempt was", async () => {
    renderMeasurementValue({
        latestMeasurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00", count: { value: null } },
    })
    await hoverText(/\?/)
    await expectTextAfterWait(/This metric was not recently measured/)
    expectText(/Last measurement attempt/)
})

it("does not show an error message for past measurements that were recently measured at the time", async () => {
    const reportDate = new Date("2022-01-16T01:00:00")
    renderMeasurementValue({
        latestMeasurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00" },
        reportDate: reportDate,
    })
    await hoverText(/\?/)
    await expectNoTextAfterWait(/This metric was not recently measured/)
    expectText(/Last measurement attempt/)
})

it("shows ignored measurement entities", async () => {
    renderMeasurementValue({
        status: "target_met",
        unit_singular: "foo",
        latestMeasurement: {
            start: "2022-01-16T00:31:00",
            end: "2022-01-16T00:51:00",
            count: { value: "1" },
            sources: [
                {
                    entities: [{ key: "entity1" }, { key: "entity2" }],
                    entity_user_data: { entity1: { status: "false_positive" }, entity2: { status: "confirmed" } },
                },
                {},
            ],
        },
    })
    await hoverText(/1/)
    await expectTextAfterWait(/Ignored foo/)
})

it("does not show ignored measurement entities that no longer exist", async () => {
    renderMeasurementValue({
        status: "target_met",
        unit_singular: "foo",
        latestMeasurement: {
            start: "2022-01-16T00:31:00",
            end: "2022-01-16T00:51:00",
            count: { value: "1" },
            sources: [
                {
                    entities: [{ key: "entity2" }],
                    entity_user_data: { entity1: { status: "false_positive" }, entity2: { status: "confirmed" } },
                },
                {},
            ],
        },
    })
    await hoverText(/1/)
    await expectNoTextAfterWait(/Ignored foo/)
})
