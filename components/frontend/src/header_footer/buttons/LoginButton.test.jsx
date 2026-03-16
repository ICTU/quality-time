import { render } from "@testing-library/react"
import { vi } from "vitest"

import * as fetchServerApi from "../../api/fetch_server_api"
import { asyncClickButton, clickButton, expectNoAccessibilityViolations, expectTextAfterWait } from "../../testUtils"
import { LoginButton } from "./LoginButton"

function renderLoginButton() {
    const setUser = vi.fn()
    render(<LoginButton setUser={setUser} />)
    return setUser
}

it("has no accessibility violations", async () => {
    const { container } = render(<LoginButton />)
    await expectNoAccessibilityViolations(container)
})

it("logs in the user", async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({
        ok: true,
        email: "user@example.org",
        session_expiration_datetime: "3000-01-01",
    })
    const setUser = renderLoginButton()
    clickButton("Login")
    await asyncClickButton("Submit")
    expect(setUser).toHaveBeenCalled()
})

it("cancels the login", async () => {
    const setUser = renderLoginButton()
    clickButton("Login")
    clickButton("Cancel")
    expect(setUser).not.toHaveBeenCalled()
})

it("fails to log in the user", () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: false })
    const setUser = renderLoginButton()
    clickButton("Login")
    clickButton("Submit")
    expectTextAfterWait("Invalid credentials")
    expect(setUser).not.toHaveBeenCalled()
})

it("reports a connection error", () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockRejectedValue(new Error("Async error message"))
    const setUser = renderLoginButton()
    clickButton("Login")
    clickButton("Submit")
    expectTextAfterWait("Connection error")
    expect(setUser).not.toHaveBeenCalled()
})
