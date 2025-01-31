import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { expectNoAccessibilityViolations } from "../testUtils"
import { UIModeMenu } from "./UIModeMenu"

const openUIModeMenu = () => fireEvent.click(screen.getByLabelText(/Dark\/light mode/))
const click = (mode) => fireEvent.click(screen.getByText(mode))

it("sets dark mode", async () => {
    const setUIMode = jest.fn()
    const { container } = render(<UIModeMenu setUIMode={setUIMode} />)
    openUIModeMenu()
    click("Dark mode")
    expect(setUIMode).toHaveBeenCalledWith("dark")
    await expectNoAccessibilityViolations(container)
})

it("sets light mode", async () => {
    const setUIMode = jest.fn()
    const { container } = render(<UIModeMenu setUIMode={setUIMode} uiMode="dark" />)
    openUIModeMenu()
    click("Light mode")
    expect(setUIMode).toHaveBeenCalledWith("light")
    await expectNoAccessibilityViolations(container)
})

it("sets follows os mode", () => {
    const setUIMode = jest.fn()
    render(<UIModeMenu setUIMode={setUIMode} uiMode="dark" />)
    openUIModeMenu()
    click("Follow OS setting")
    expect(setUIMode).toHaveBeenCalledWith("system")
})

it("sets dark mode on keypress", async () => {
    const setUIMode = jest.fn()
    render(<UIModeMenu setUIMode={setUIMode} uiMode="light" />)
    openUIModeMenu()
    await userEvent.type(screen.getByText(/Dark mode/), " ")
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("closes the menu on escape", async () => {
    const setUIMode = jest.fn()
    render(<UIModeMenu setUIMode={setUIMode} />)
    openUIModeMenu()
    await userEvent.keyboard("{Escape}")
    expect(setUIMode).not.toHaveBeenCalled()
})
