import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { DataModel } from "../context/DataModel"
import { MeasurementValue } from "./MeasurementValue"

function renderMeasurementValue({
    latest_measurement = {},
    reportDate = null,
    scale = "count",
    status = null,
    type = "violations",
    unit = null,
} = {}) {
    render(
        <DataModel.Provider value={{ metrics: { violations: { unit: "violations" } } }}>
            <MeasurementValue
                metric={{
                    latest_measurement: latest_measurement,
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

it("renders the value", () => {
    renderMeasurementValue({ latest_measurement: { count: { value: "42" } } })
    expect(screen.getAllByText(/42/).length).toBe(1)
})

it("renders an unkown value", () => {
    renderMeasurementValue({ latest_measurement: { count: { value: null } } })
    expect(screen.getAllByText(/\?/).length).toBe(1)
})

it("renders a value that has not been measured yet", () => {
    renderMeasurementValue()
    expect(screen.getAllByText(/\?/).length).toBe(1)
})

it("renders an outdated value", async () => {
    renderMeasurementValue({
        latest_measurement: {
            count: { value: 1 },
            outdated: true,
            start: new Date().toISOString(),
            end: new Date().toISOString(),
        },
    })
    const measurementValue = screen.getByText(/1/)
    expect(measurementValue.className).toContain("yellow")
    expect(measurementValue.children[0].className).toContain("loading")
    await userEvent.hover(measurementValue)
    await waitFor(() => {
        expect(screen.queryByText(/Latest measurement out of date/)).not.toBe(null)
        expect(
            screen.queryByText(/The source configuration of this metric was changed after the latest measurement/),
        ).not.toBe(null)
    })
})

it("renders a minutes value", () => {
    renderMeasurementValue({
        type: "duration",
        latest_measurement: { count: { value: "42" } },
    })
    expect(screen.getAllByText(/42/).length).toBe(1)
})

it("renders an unknown minutes value", () => {
    renderMeasurementValue({
        type: "duration",
        latest_measurement: { count: { value: null } },
    })
    expect(screen.getAllByText(/\?/).length).toBe(1)
})

it("renders a minutes percentage", () => {
    renderMeasurementValue({
        type: "duration",
        scale: "percentage",
        latest_measurement: { percentage: { value: "42" } },
    })
    expect(screen.getAllByText(/42%/).length).toBe(1)
})

it("renders an unknown minutes percentage", () => {
    renderMeasurementValue({
        type: "duration",
        scale: "percentage",
        latest_measurement: { percentage: { value: null } },
    })
    expect(screen.getAllByText(/\?%/).length).toBe(1)
})

it("shows when the metric was last measured", async () => {
    renderMeasurementValue({
        status: "target_met",
        latest_measurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00", count: { value: "42" } },
    })
    await userEvent.hover(screen.queryByText(/42/))
    await waitFor(() => {
        expect(screen.queryByText(/The metric was last measured/)).not.toBe(null)
    })
})

it("shows when the last measurement attempt was", async () => {
    renderMeasurementValue({
        latest_measurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00", count: { value: null } },
    })
    await userEvent.hover(screen.queryByText(/\?/))
    await waitFor(() => {
        expect(screen.queryByText(/This metric was not recently measured/)).not.toBe(null)
        expect(screen.queryByText(/Last measurement attempt/)).not.toBe(null)
    })
})

it("does not show an error message for past measurements that were recently measured at the time", async () => {
    const reportDate = new Date("2022-01-16T01:00:00")
    renderMeasurementValue({
        latest_measurement: { start: "2022-01-16T00:31:00", end: "2022-01-16T00:51:00" },
        reportDate: reportDate,
    })
    await userEvent.hover(screen.queryByText(/\?/))
    await waitFor(() => {
        expect(screen.queryByText(/This metric was not recently measured/)).toBe(null)
        expect(screen.queryByText(/Last measurement attempt/)).not.toBe(null)
    })
})
