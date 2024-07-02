import { render, screen } from "@testing-library/react"

import { DarkMode } from "../context/DarkMode"
import { DataModel } from "../context/DataModel"
import { TrendGraph } from "./TrendGraph"

const dataModel = {
    metrics: {
        stability: { name: "Stability", unit: "minutes", direction: ">", tags: [] },
        violations: { name: "Violations", unit: "violations", direction: "<", tags: [] },
    },
}

function renderTrendgraph({ measurements = [], darkMode = false, scale = "count", loading = "loaded" } = {}) {
    return render(
        <DarkMode.Provider value={darkMode}>
            <DataModel.Provider value={dataModel}>
                <TrendGraph
                    metric={{ type: "violations", scale: scale }}
                    measurements={measurements}
                    loading={loading}
                />
            </DataModel.Provider>
        </DarkMode.Provider>,
    )
}

it("renders the measurements", () => {
    renderTrendgraph({
        measurements: [{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }],
    })
    expect(screen.getAllByText(/Time/).length).toBe(1)
})

it("renders the measurements in dark mode", () => {
    renderTrendgraph({
        measurements: [{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }],
        darkMode: true,
    })
    expect(screen.getAllByText(/Time/).length).toBe(1)
})

it("renders measurements with targets", () => {
    renderTrendgraph({
        measurements: [
            {
                count: { value: "1", target: "10", near_target: "20" },
                start: "2019-09-29",
                end: "2019-09-30",
            },
        ],
    })
    expect(screen.getAllByText(/Time/).length).toBe(1)
})

it("renders the measurements with zero length", () => {
    renderTrendgraph({
        measurements: [{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-29" }],
    })
    expect(screen.getAllByText(/Time/).length).toBe(1)
})

it("renders the measurements with missing values for the scale", () => {
    renderTrendgraph({
        measurements: [{ percentage: { value: "1" }, start: "2019-09-29", end: "2019-09-29" }],
    })
    expect(screen.getAllByText(/Time/).length).toBe(1)
})

it("renders a placeholder while the measurements are loading", () => {
    const { container } = renderTrendgraph({ loading: "loading" })
    expect(container.firstChild.className).toContain("placeholder")
    expect(screen.queryAllByText(/Time/).length).toBe(0)
})

it("renders a message if the measurements failed to load", () => {
    renderTrendgraph({ loading: "failed" })
    expect(screen.getAllByText(/Loading measurements failed/).length).toBe(1)
})

it("renders a message if the metric scale is version number", () => {
    renderTrendgraph({ scale: "version_number" })
    expect(screen.queryAllByText(/Time/).length).toBe(0)
    expect(screen.getAllByText(/version number scale/).length).toBe(1)
})

it("renders a message if the metric has no measurements", () => {
    renderTrendgraph()
    expect(screen.queryAllByText(/Time/).length).toBe(0)
    expect(screen.getAllByText(/trend graph can not be displayed/).length).toBe(1)
})
