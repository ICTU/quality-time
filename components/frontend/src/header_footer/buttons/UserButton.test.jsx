import { fireEvent, render } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../../api/fetch_server_api"
import { clickButton, clickMenuItem } from "../../testUtils"
import { UserButton } from "./UserButton"

beforeAll(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi")
})

function renderUserButton() {
    const setUser = vi.fn()
    render(<UserButton user="jadoe" email="jadoe@example.org" setUser={setUser} />)
    return setUser
}

it("logs out the user when clicking the log out menu item", () => {
    const setUser = renderUserButton()
    clickButton()
    clickMenuItem()
    expect(setUser).toHaveBeenCalled()
})

it("does not log out the user when closing the menu by clicking the button twice", () => {
    const setUser = renderUserButton()
    const button = clickButton()
    fireEvent.click(button)
    expect(setUser).not.toHaveBeenCalled()
})

it("does not log out the user when closing the menu by typing escape", async () => {
    const setUser = renderUserButton()
    clickButton()
    await userEvent.keyboard("{Escape}")
    expect(setUser).not.toHaveBeenCalled()
})
