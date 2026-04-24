import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { clickButton, expectNoAccessibilityViolations } from "../testUtils"
import { TrendSparkline } from "./TrendSparkline"

it("has no accessibility violations", async () => {
    const { container } = render(
        <TrendSparkline
            measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]}
            scale="count"
        />,
    )
    await expectNoAccessibilityViolations(container)
})

it("returns null when the metric scale is version number", async () => {
    render(<TrendSparkline scale="version_number" />)
    expect(screen.queryAllByLabelText(/sparkline graph/).length).toBe(0)
})

it("renders an empty sparkline if there are no measurements", async () => {
    render(<TrendSparkline />)
    expect(screen.queryAllByLabelText(/sparkline graph showing 0 different measurement values/).length).toBe(1)
})

it("renders a recent measurement", async () => {
    render(
        <TrendSparkline
            measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]}
            scale="count"
        />,
    )
    expect(
        screen.queryAllByLabelText(/sparkline graph showing 1 different measurement value in the week before today/)
            .length,
    ).toBe(1)
})

it("renders multiple recent measurements", async () => {
    render(
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
})

it("renders old measurements", async () => {
    const date = new Date("2020-01-01")
    render(
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
})

it("has no accessibility violations when clickable", async () => {
    const { container } = render(
        <TrendSparkline
            measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]}
            onClick={() => {}}
            scale="count"
        />,
    )
    await expectNoAccessibilityViolations(container)
})

it("does not render a button when onClick is not provided", async () => {
    render(<TrendSparkline measurements={[]} scale="count" />)
    expect(screen.queryByRole("button")).toBeNull()
})

it("renders a button when onClick is provided", async () => {
    const onClick = vi.fn()
    render(<TrendSparkline measurements={[]} onClick={onClick} scale="count" />)
    expect(screen.getByRole("button", { name: /show trend graph/i })).toBeInTheDocument()
})

it("invokes onClick when the button is clicked", async () => {
    const onClick = vi.fn()
    render(<TrendSparkline measurements={[]} onClick={onClick} scale="count" />)
    clickButton(/show trend graph/i)
    expect(onClick).toHaveBeenCalledTimes(1)
})

it("invokes onClick when the button is activated with the space key", async () => {
    const onClick = vi.fn()
    render(<TrendSparkline measurements={[]} onClick={onClick} scale="count" />)
    const button = screen.getByRole("button", { name: /show trend graph/i })
    button.focus()
    await userEvent.keyboard(" ")
    expect(onClick).toHaveBeenCalledTimes(1)
})

it("invokes onClick when the button is activated with the enter key", async () => {
    const onClick = vi.fn()
    render(<TrendSparkline measurements={[]} onClick={onClick} scale="count" />)
    const button = screen.getByRole("button", { name: /show trend graph/i })
    button.focus()
    await userEvent.keyboard("{Enter}")
    expect(onClick).toHaveBeenCalledTimes(1)
})
