import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { LabelWithDropdown } from "./LabelWithDropdown"

function renderLabelWithDropdown() {
    const mockCallback = jest.fn()
    render(
        <LabelWithDropdown
            label="Hello"
            onChange={mockCallback}
            options={[
                { key: "1", value: "1", text: "Option 1", color: "black" },
                { key: "2", value: "2", text: "Option 2", color: "orange" },
            ]}
            value="1"
        />,
    )
    return mockCallback
}

it("shows the label", () => {
    renderLabelWithDropdown()
    expect(screen.getByText(/Hello/)).not.toBe(null)
})

it("changes the option", async () => {
    const mockCallback = renderLabelWithDropdown()
    await userEvent.click(screen.getByText(/Option 1/))
    await userEvent.click(screen.getByText(/Option 2/))
    expect(mockCallback).toHaveBeenCalledWith("2")
})
