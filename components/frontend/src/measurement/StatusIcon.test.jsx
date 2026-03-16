import { render } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { expectNoAccessibilityViolations, expectTextAfterWait } from "../testUtils"
import { StatusIcon } from "./StatusIcon"

it("has no accessibility violations", async () => {
    const { container } = render(<StatusIcon status="informative" />)
    await expectNoAccessibilityViolations(container)
})

it("renders a checkmark if the status is target met", async () => {
    const { getAllByLabelText } = render(<StatusIcon status="target_met" />)
    expect(getAllByLabelText(/Target met/).length).toBe(1)
})

it("renders an info icon if the status is informative", async () => {
    const { getAllByLabelText } = render(<StatusIcon status="informative" />)
    expect(getAllByLabelText(/Informative/).length).toBe(1)
})

it("renders a question mark if the status is missing", async () => {
    const { getAllByLabelText } = render(<StatusIcon />)
    expect(getAllByLabelText(/Unknown/).length).toBe(1)
})

it("renders a popup with the date the status started", async () => {
    let startDate = new Date()
    startDate.setDate(startDate.getDate() - 4)
    const { queryByLabelText } = render(<StatusIcon status="target_met" statusStart={startDate} />)
    await userEvent.hover(queryByLabelText(/Target met/))
    await expectTextAfterWait(/4 days ago/)
})
