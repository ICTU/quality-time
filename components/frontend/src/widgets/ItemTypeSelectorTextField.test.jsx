import { fireEvent, render, screen } from "@testing-library/react"
import { vi } from "vitest"

import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { ItemTypeSelectorTextField } from "./ItemTypeSelectorTextField"

function renderItemTypeSelectorTextField({ disabled = false, handleMenu = vi.fn(), startAdornment = null } = {}) {
    return render(
        <ItemTypeSelectorTextField
            disabled={disabled}
            handleMenu={handleMenu}
            helperText="Help text"
            label="Item type"
            startAdornment={startAdornment}
            value="Item value"
        />,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderItemTypeSelectorTextField()
    await expectNoAccessibilityViolations(container)
})

it("shows the label, value, and helper text", () => {
    renderItemTypeSelectorTextField()
    expect(screen.getByLabelText("Item type")).toHaveValue("Item value")
    expectText("Help text")
})

it("is read-only", () => {
    renderItemTypeSelectorTextField()
    expect(screen.getByDisplayValue("Item value")).toHaveAttribute("readonly")
})

it("shows the dropdown arrow", () => {
    renderItemTypeSelectorTextField()
    expect(screen.getByTestId("ArrowDropDownIcon")).toBeInTheDocument()
})

it("shows the start adornment when given", () => {
    renderItemTypeSelectorTextField({ startAdornment: <span>Start</span> })
    expectText("Start")
})

it("opens the menu when clicked", () => {
    const handleMenu = vi.fn()
    renderItemTypeSelectorTextField({ handleMenu })
    fireEvent.click(screen.getByDisplayValue("Item value"))
    expect(handleMenu).toHaveBeenCalled()
})

it("does not open the menu when clicked while disabled", () => {
    const handleMenu = vi.fn()
    renderItemTypeSelectorTextField({ disabled: true, handleMenu })
    fireEvent.click(screen.getByDisplayValue("Item value"))
    expect(handleMenu).not.toHaveBeenCalled()
})

for (const key of ["Enter", " ", "ArrowDown", "ArrowUp"]) {
    it(`opens the menu when pressing "${key}"`, () => {
        const handleMenu = vi.fn()
        renderItemTypeSelectorTextField({ handleMenu })
        const defaultNotPrevented = fireEvent.keyDown(screen.getByDisplayValue("Item value"), { key: key })
        expect(handleMenu).toHaveBeenCalled()
        expect(defaultNotPrevented).toBe(false) // The handler calls preventDefault
    })
}

it("does not open the menu when pressing another key", () => {
    const handleMenu = vi.fn()
    renderItemTypeSelectorTextField({ handleMenu })
    fireEvent.keyDown(screen.getByDisplayValue("Item value"), { key: "a" })
    expect(handleMenu).not.toHaveBeenCalled()
})

it("does not open the menu when pressing a key while disabled", () => {
    const handleMenu = vi.fn()
    renderItemTypeSelectorTextField({ disabled: true, handleMenu })
    fireEvent.keyDown(screen.getByDisplayValue("Item value"), { key: "Enter" })
    expect(handleMenu).not.toHaveBeenCalled()
})
