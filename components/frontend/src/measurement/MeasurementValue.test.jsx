import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations } from "../testUtils"
import { MeasurementValue } from "./MeasurementValue"

function renderMeasurementValue({
    latest_measurement = {},
    measurement_requested = null,
    reportDate = null,
    scale = "count",
    status = null,
    type = "violations",
    unit = null,
} = {}) {
    return render(
        <DataModel.Provider value={{ metrics: { violations: { unit: "violations" } } }}>
            <MeasurementValue
                metric={{
                    latest_measurement: latest_measurement,
                    measurement_requested: measurement_requested,
                    scale: scale,
                    status: status,
                    type: type,
                    unit: unit,
                }}
                reportDate={reportDate}
            />
        </DataModel.Provider>,
    )
}

it("renders the value", async () => {
    const { container } = renderMeasurementValue({ latest_measurement: { count: { value: "42" } } })
    expect(screen.getAllByText(/42/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders an unkown value", async () => {
    const { container } = renderMeasurementValue({ latest_measurement: { count: { value: null } } })
    expect(screen.getAllByText(/\?/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a value that has not been measured yet", async () => {
    const { container } = renderMeasurementValue()
    expect(screen.getAllByText(/\?/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders an outdated value", async () => {
    const { container } = renderMeasurementValue({
        latest_measurement: {
            count: { value: 1 },
            outdated: true,
            start: new Date().toISOString(),
            end: new Date().toISOString(),
        },
    })
    const measurementValue = screen.getByText(/1/)
    expect(screen.getAllByTestId("LoopIcon").length).toBe(1)
    await userEvent.hover(measurementValue)
    await waitFor(() => {
        expect(screen.queryByText(/Latest measurement out of date/)).not.toBe(null)
        expect(
            screen.queryByText(/The source configuration of this metric was changed after the latest measurement/),
        ).not.toBe(null)
    })
    await expectNoAccessibilityViolations(container)
})

it("renders a value for which a measurement was requested", async () => {
    const now = new Date().toISOString()
    const { container } = renderMeasurementValue({
        latest_measurement: { count: { value: 1 }, start: now, end: now },
        measurement_requested: now,
    })
    const measurementValue = screen.getByText(/1/)
    expect(screen.getAllByTestId("LoopIcon").length).toBe(1)
    await userEvent.hover(measurementValue)
    await waitFor(() => {
        expect(screen.queryByText(/Measurement requested/)).not.toBe(null)
        expect(screen.queryByText(/An update of the latest measurement was requested by a user/)).not.toBe(null)
    })
    await expectNoAccessibilityViolations(container)
})

it("renders a value for which a measurement was requested, but which is now up to date", async () => {
    const now = new Date().toISOString()
    const { container } = renderMeasurementValue({
        latest_measurement: { count: { value: 1 }, start: now, end: now },
        measurement_requested: "2024-01-01T00:00:00",
    })
    const measurementValue = screen.getByText(/1/)
    expect(screen.queryAllByTestId("LoopIcon").length).toBe(0)
    await userEvent.hover(measurementValue)
    await waitFor(async () => {
        expect(screen.queryByText(/Measurement requested/)).toBe(null)
        expect(screen.queryByText(/An update of the latest measurement was requested by a user/)).toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("renders a minutes value", async () => {
    const { container } = renderMeasurementValue({
        type: "duration",
        unit: "foo units",
        latest_measurement: { count: { value: "42" } },
    })
    expect(screen.getAllByText(/42/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders an unknown minutes value", async () => {
    const { container } = renderMeasurementValue({
        type: "duration",
        unit: "foo units",
        latest_measurement: { count: { value: null } },
    })
    expect(screen.getAllByText(/\?/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a minutes percentage", async () => {
    const { container } = renderMeasurementValue({
        type: "duration",
        scale: "percentage",
        unit: "foo units",
        latest_measurement: { percentage: { value: "42" } },
    })
    expect(screen.getAllByText(/42%/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders an unknown minutes percentage", async () => {
    const { container } = renderMeasurementValue({
        type: "duration",
        scale: "percentage",
        unit: "foo units",
        latest_measurement: { percentage: { value: null } },
    })
    expect(screen.getAllByText(/\?%/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows when the metric was last measured", async () => {
    const { container } = renderMeasurementValue({
        status: "target_met",
        latest_measurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00", count: { value: "42" } },
    })
    await userEvent.hover(screen.queryByText(/42/))
    await waitFor(async () => {
        expect(screen.queryByText(/The metric was last measured/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("shows when the last measurement attempt was", async () => {
    const { container } = renderMeasurementValue({
        latest_measurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00", count: { value: null } },
    })
    await userEvent.hover(screen.queryByText(/\?/))
    await waitFor(async () => {
        expect(screen.queryByText(/This metric was not recently measured/)).not.toBe(null)
        expect(screen.queryByText(/Last measurement attempt/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("does not show an error message for past measurements that were recently measured at the time", async () => {
    const reportDate = new Date("2022-01-16T01:00:00")
    const { container } = renderMeasurementValue({
        latest_measurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00" },
        reportDate: reportDate,
    })
    await userEvent.hover(screen.queryByText(/\?/))
    await waitFor(async () => {
        expect(screen.queryByText(/This metric was not recently measured/)).toBe(null)
        expect(screen.queryByText(/Last measurement attempt/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("shows ignored measurement entities", async () => {
    const { container } = renderMeasurementValue({
        status: "target_met",
        unit: "foo",
        latest_measurement: {
            start: "2022-01-16T00:31:00",
            end: "2022-01-16T00:51:00",
            count: { value: "42" },
            sources: [
                { entity_user_data: { entity1: { status: "false_positive" }, entity2: { status: "confirmed" } } },
                {},
            ],
        },
    })
    await userEvent.hover(screen.queryByText(/42/))
    await waitFor(async () => {
        expect(screen.queryByText(/Ignored foo/)).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})
