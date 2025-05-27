import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations } from "../testUtils"
import { TrendGraph } from "./TrendGraph"

const dataModel = {
    metrics: {
        stability: { name: "Stability", unit: "minutes", direction: ">", tags: [] },
        violations: { name: "Violations", unit: "violations", direction: "<", tags: [] },
    },
}

function renderTrendgraph({ measurements = [], scale = "count", loading = "loaded" } = {}) {
    return render(
        <DataModel.Provider value={dataModel}>
            <TrendGraph metric={{ type: "violations", scale: scale }} measurements={measurements} loading={loading} />
        </DataModel.Provider>,
    )
}

it("renders the measurements", async () => {
    const { container } = renderTrendgraph({
        measurements: [{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }],
    })
    expect(screen.getAllByText(/Time/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders the tooltip", async () => {
    // Mock the getScreenCTM function, see https://docs.jointjs.com/learn/testing/jest/#jsdom-and-svg-apis
    const createSVGMatrix = () => ({
        inverse: vi.fn().mockImplementation(createSVGMatrix),
    })
    Object.defineProperty(globalThis.SVGElement.prototype, "getScreenCTM", {
        writable: true,
        value: vi.fn().mockImplementation(createSVGMatrix),
    })
    const { container } = renderTrendgraph({
        measurements: [{ count: { value: "1", status: "target_met" }, start: "2019-09-29", end: "2019-09-30" }],
    })
    userEvent.hover(screen.getAllByTestId(/Point/)[0])
    await waitFor(async () => {
        expect(screen.getAllByText(/1 violations \(target met\) on/).length).toBe(1)
    })
    await expectNoAccessibilityViolations(container)
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
    expect(container.firstChild.className).toContain("MuiSkeleton-rectangular")
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
