import { render, screen } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations } from "../testUtils"
import { Overrun } from "./Overrun"

const dates = [new Date("2020-01-01"), new Date("2020-12-31")]

const dataModel = {
    metrics: {
        metric_type: {
            default_scale: "count",
        },
    },
}

function renderOverrun({ measurements = [], dates = [] } = {}) {
    return render(
        <DataModel.Provider value={dataModel}>
            <Overrun dates={dates} metric={{ type: "metric_type" }} metric_uuid="uuid" measurements={measurements} />
        </DataModel.Provider>,
    )
}

it("renders nothing if there is no overrun", async () => {
    const { container } = renderOverrun()
    expect(screen.queryAllByDisplayValue(/days/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders the days overrun if the metric has overrun its deadline", async () => {
    const { container } = renderOverrun({
        dates: dates,
        measurements: [{ metric_uuid: "uuid", start: "2020-01-01", end: "2020-01-31" }],
    })
    expect(screen.queryAllByText(/27 days/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("merges the days overrun if the metric has consecutive measurements", async () => {
    const { container } = renderOverrun({
        dates: dates,
        measurements: [
            { metric_uuid: "uuid", start: "2020-01-01", end: "2020-01-10" },
            { metric_uuid: "uuid", start: "2020-01-10", end: "2020-01-20" },
        ],
    })
    expect(screen.queryAllByText(/16 days/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})
