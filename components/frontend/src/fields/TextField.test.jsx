import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { expectNoAccessibilityViolations } from "../testUtils"
import { TextField } from "./TextField"

function renderTextField({ onChange = vi.fn(), placeholder = null, required = false, type = null, value = null } = {}) {
    return render(
        <TextField onChange={onChange} placeholder={placeholder} required={required} type={type} value={value} />,
    )
}

async function typeInField(text, confirm = "Enter") {
    const element = screen.queryAllByRole("textbox")[0] ?? screen.getByRole("spinbutton")
    await userEvent.type(element, `${text}{${confirm}}`, {
        initialSelectionStart: 0,
        initialSelectionEnd: 100,
    })
}

it("has no accessibility violations", async () => {
    const { container } = renderTextField({ placeholder: "placeholder" })
    await expectNoAccessibilityViolations(container)
})

it("sets the value on enter", async () => {
    const onChange = vi.fn()
    renderTextField({ onChange: onChange })
    await typeInField("New value")
    expect(onChange).toHaveBeenCalledWith("New value")
})

it("sets the value on tab", async () => {
    const onChange = vi.fn()
    renderTextField({ onChange: onChange })
    await typeInField("New value", "Tab")
    expect(onChange).toHaveBeenCalledWith("New value")
})

it("sets an empty value", async () => {
    const onChange = vi.fn()
    renderTextField({ onChange: onChange, value: "Some value" })
    await typeInField("{Delete}", "Enter")
    expect(onChange).toHaveBeenCalledWith("")
})

it("doesn't set the value if it's unchanged", async () => {
    const onChange = vi.fn()
    renderTextField({ onChange: onChange })
    await typeInField("")
    expect(onChange).not.toHaveBeenCalled()
})

it("doesn't set an empty value if a non-empty value is required", async () => {
    const onChange = vi.fn()
    renderTextField({ onChange: onChange, required: true })
    await typeInField("")
    expect(onChange).not.toHaveBeenCalled()
})

it("resets the value on escape", async () => {
    const onChange = vi.fn()
    renderTextField({ onChange: onChange })
    await typeInField("New value{Escape}")
    await typeInField("{Enter}")
    expect(onChange).not.toHaveBeenCalled()
})

it("doesn't set an invalid number value", async () => {
    const onChange = vi.fn()
    renderTextField({ onChange: onChange, required: true, type: "number" })
    await typeInField("not a number")
    expect(onChange).not.toHaveBeenCalled()
})
