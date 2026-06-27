import { render, screen } from "@testing-library/react"
import { vi } from "vitest"

import { asyncClickText, expectText } from "../../testUtils"
import { AddItemByTypeButton } from "./AddItemByTypeButton"

function renderAddItemByTypeButton() {
    const mockCallback = vi.fn()
    const itemSubtypes = [
        { key: "sub 1", text: "Sub 1", value: "sub 1", content: "Sub 1" },
        { key: "sub 2", text: "Sub 2", value: "sub 2", content: "Sub 2" },
    ]
    render(<AddItemByTypeButton itemType="foo" itemSubtypes={itemSubtypes} onClick={mockCallback} />)
    return mockCallback
}

it("shows the button", () => {
    renderAddItemByTypeButton()
    expectText(/Add foo/)
})

it("opens the menu and selects an item", async () => {
    const mockCallback = renderAddItemByTypeButton()
    await asyncClickText(/Add foo/)
    expect(screen.getByLabelText(/Filter/)).toHaveFocus()
    await asyncClickText(/Sub 2/)
    expect(mockCallback).toHaveBeenCalledWith("sub 2")
})
