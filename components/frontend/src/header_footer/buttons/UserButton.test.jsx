import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { UserButton } from "./UserButton"

vi.mock("../../api/auth.js")

function renderUserButton() {
    const setUser = vi.fn()
    render(<UserButton user="jadoe" email="jadoe@example.org" setUser={setUser} />)
    return setUser
}

it("logs out the user when clicking the log out menu item", () => {
    const setUser = renderUserButton()
    fireEvent.click(screen.getByRole("button"))
    fireEvent.click(screen.getByRole("menuitem"))
    expect(setUser).toHaveBeenCalled()
})

it("does not log out the user when closing the menu by clicking the button twice", () => {
    const setUser = renderUserButton()
    const button = screen.getByRole("button")
    fireEvent.click(button)
    fireEvent.click(button)
    expect(setUser).not.toHaveBeenCalled()
})

it("does not log out the user when closing the menu by typing escape", async () => {
    const setUser = renderUserButton()
    const button = screen.getByRole("button")
    fireEvent.click(button)
    await userEvent.keyboard("{Escape}")
    expect(setUser).not.toHaveBeenCalled()
})
