import { render, screen } from "@testing-library/react"

import { expectNoAccessibilityViolations } from "../testUtils"
import { TrendSparkline } from "./TrendSparkline"

it("returns null when the metric scale is version number", async () => {
    const { container } = render(<TrendSparkline scale="version_number" />)
    expect(screen.queryAllByLabelText(/sparkline graph/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders an empty sparkline if there are no measurements", async () => {
    const { container } = render(<TrendSparkline />)
    expect(screen.queryAllByLabelText(/sparkline graph showing 0 different measurement values/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a recent measurement", async () => {
    const { container } = render(
        <TrendSparkline
            measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]}
            scale="count"
        />,
    )
    expect(
        screen.queryAllByLabelText(/sparkline graph showing 1 different measurement value in the week before today/)
            .length,
    ).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders multiple recent measurements", async () => {
    const { container } = render(
        <TrendSparkline
            measurements={[
                { count: { value: null }, start: "2019-09-27", end: "2019-09-28" },
                { count: { value: "1" }, start: "2019-09-28", end: "2019-09-29" },
                { count: { value: "2" }, start: "2019-09-29", end: "2019-09-30" },
            ]}
            scale="count"
        />,
    )
    expect(
        screen.queryAllByLabelText(/sparkline graph showing 2 different measurement values in the week before today/)
            .length,
    ).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders old measurements", async () => {
    const date = new Date("2020-01-01")
    const { container } = render(
        <TrendSparkline
            measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]}
            reportDate={date}
            scale="count"
        />,
    )
    expect(
        screen.queryAllByLabelText(
            `sparkline graph showing 1 different measurement value in the week before ${date.toLocaleDateString()}`,
        ).length,
    ).toBe(1)
    await expectNoAccessibilityViolations(container)
})
