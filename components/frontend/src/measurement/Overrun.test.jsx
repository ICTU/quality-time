import { render, screen } from "@testing-library/react"

import { DataModelContext } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectText } from "../testUtils"
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
        <DataModelContext value={dataModel}>
            <Overrun dates={dates} metric={{ type: "metric_type" }} metricUuid="uuid" measurements={measurements} />
        </DataModelContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderOverrun({
        dates: dates,
        measurements: [{ metric_uuid: "uuid", start: "2020-01-01", end: "2020-01-31" }],
    })
    await expectNoAccessibilityViolations(container)
})

it("renders nothing if there is no overrun", async () => {
    renderOverrun()
    expect(screen.queryAllByDisplayValue(/days/).length).toBe(0)
})

it("renders the days overrun if the metric has overrun its deadline", async () => {
    renderOverrun({
        dates: dates,
        measurements: [{ metric_uuid: "uuid", start: "2020-01-01", end: "2020-01-31" }],
    })
    expectText(/27 days/)
})

it("merges the days overrun if the metric has consecutive measurements", async () => {
    renderOverrun({
        dates: dates,
        measurements: [
            { metric_uuid: "uuid", start: "2020-01-01", end: "2020-01-10" },
            { metric_uuid: "uuid", start: "2020-01-10", end: "2020-01-20" },
        ],
    })
    expectText(/16 days/)
})
