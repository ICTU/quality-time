import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { clickLabeledElement, clickText, expectNoAccessibilityViolations } from "../testUtils"
import { UIModeMenu } from "./UIModeMenu"

const openUIModeMenu = () => clickLabeledElement(/Dark\/light mode/)

it("has no accessibility violations", async () => {
    const { container } = render(<UIModeMenu />)
    await expectNoAccessibilityViolations(container)
})

it("sets dark mode", async () => {
    const setUIMode = vi.fn()
    render(<UIModeMenu setUIMode={setUIMode} />)
    openUIModeMenu()
    clickText("Dark mode")
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("sets light mode", async () => {
    const setUIMode = vi.fn()
    render(<UIModeMenu setUIMode={setUIMode} uiMode="dark" />)
    openUIModeMenu()
    clickText("Light mode")
    expect(setUIMode).toHaveBeenCalledWith("light")
})

it("sets follows os mode", () => {
    const setUIMode = vi.fn()
    render(<UIModeMenu setUIMode={setUIMode} uiMode="dark" />)
    openUIModeMenu()
    clickText("Follow OS setting")
    expect(setUIMode).toHaveBeenCalledWith("system")
})

it("sets dark mode on keypress", async () => {
    const setUIMode = vi.fn()
    render(<UIModeMenu setUIMode={setUIMode} uiMode="light" />)
    openUIModeMenu()
    await userEvent.type(screen.getByText(/Dark mode/), " ")
    expect(setUIMode).toHaveBeenCalledWith("dark")
})

it("closes the menu on escape", async () => {
    const setUIMode = vi.fn()
    render(<UIModeMenu setUIMode={setUIMode} />)
    openUIModeMenu()
    await userEvent.keyboard("{Escape}")
    expect(setUIMode).not.toHaveBeenCalled()
})
