import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { expectNoAccessibilityViolations } from "../testUtils"
import { Menubar } from "./Menubar"

vi.mock("../api/fetch_server_api.js")

beforeEach(() => history.push(""))

afterEach(() => vi.resetAllMocks())

const CREDENTIALS = { username: "user@example.org", password: "secret" }

function renderMenubar({
    openReportsOverview = null,
    panel = null,
    reportUuid = "report_uuid",
    setUser = null,
    user = null,
} = {}) {
    const settings = createTestableSettings()
    return render(
        <Menubar
            onDate={vi.fn()}
            openReportsOverview={openReportsOverview}
            panel={panel}
            reportUuid={reportUuid}
            settings={settings}
            setUser={setUser}
            user={user}
        />,
    )
}

async function enterCredentials(container) {
    fireEvent.click(screen.getByText(/Login/))
    await expectNoAccessibilityViolations(container)
    fireEvent.change(screen.getByLabelText("Username"), { target: { value: CREDENTIALS.username } })
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: CREDENTIALS.password } })
    await act(async () => fireEvent.click(screen.getByText(/Submit/)))
}

it("logs in", async () => {
    fetchServerApi.fetchServerApi = vi.fn().mockResolvedValue({
        ok: true,
        email: "user@example.org",
        session_expiration_datetime: "2021-02-24T13:10:00+00:00",
    })
    const setUser = vi.fn()
    const { container } = renderMenubar({ setUser: setUser })
    await enterCredentials(container)
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith("post", "login", CREDENTIALS)
    const expectedDate = new Date(Date.parse("2021-02-24T13:10:00+00:00"))
    expect(setUser).toHaveBeenCalledWith("user@example.org", "user@example.org", expectedDate)
    await expectNoAccessibilityViolations(container)
})

it("shows invalid credential message", async () => {
    fetchServerApi.fetchServerApi = vi.fn().mockResolvedValue({ ok: false })
    const setUser = vi.fn()
    const { container } = renderMenubar({ setUser: setUser })
    await enterCredentials(container)
    expect(screen.getAllByText(/Invalid credentials/).length).toBe(1)
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith("post", "login", CREDENTIALS)
    expect(setUser).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("shows connection error message", async () => {
    fetchServerApi.fetchServerApi = vi.fn().mockRejectedValue(new Error("Async error message"))
    const setUser = vi.fn()
    const { container } = renderMenubar({ setUser: setUser })
    await enterCredentials(container)
    expect(screen.getAllByText(/Connection error/).length).toBe(1)
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith("post", "login", CREDENTIALS)
    expect(setUser).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("closes the dialog on cancel", async () => {
    const setUser = vi.fn()
    const { container } = renderMenubar({ setUser: setUser })
    fireEvent.click(screen.getByText(/Login/))
    await act(async () => fireEvent.click(screen.getByText(/Cancel/)))
    await waitFor(async () => {
        expect(screen.queryAllByLabelText("Username").length).toBe(0)
        await expectNoAccessibilityViolations(container)
    })
    expect(setUser).not.toHaveBeenCalled()
})

it("closes the dialog on escape", async () => {
    const setUser = vi.fn()
    renderMenubar({ setUser: setUser })
    fireEvent.click(screen.getByText(/Login/))
    await userEvent.keyboard("{Escape}")
    await waitFor(() => {
        expect(screen.queryAllByLabelText("Username").length).toBe(0)
    })
    expect(setUser).not.toHaveBeenCalled()
})

it("logs out", async () => {
    fetchServerApi.fetchServerApi = vi.fn().mockResolvedValue({ ok: true })
    const setUser = vi.fn()
    const { container } = renderMenubar({ setUser: setUser, user: "jadoe" })
    fireEvent.click(screen.getByRole("button", { name: "User options" }))
    fireEvent.click(screen.getByRole("menuitem", { name: "Logout" }))
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith("post", "logout", {})
    expect(setUser).toHaveBeenCalledWith(null)
    await expectNoAccessibilityViolations(container)
})

it("does not go to home page if on reports overview", async () => {
    const openReportsOverview = vi.fn()
    const { container } = renderMenubar({ reportUuid: "", openReportsOverview: openReportsOverview })
    act(() => {
        fireEvent.click(screen.getByAltText(/Go to reports overview/))
    })
    expect(openReportsOverview).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("goes to home page if on report", async () => {
    const openReportsOverview = vi.fn()
    const { container } = renderMenubar({ openReportsOverview: openReportsOverview })
    await act(async () => {
        fireEvent.click(screen.getByAltText(/Go to reports overview/))
    })
    expect(openReportsOverview).toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("goes to home page on keypress", async () => {
    const openReportsOverview = vi.fn()
    renderMenubar({ openReportsOverview: openReportsOverview })
    await userEvent.type(screen.getByAltText(/Go to reports overview/), "{Enter}")
    expect(openReportsOverview).toHaveBeenCalled()
})

it("shows the view panel on menu item click", async () => {
    const { container } = renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/))
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the view panel on space", async () => {
    renderMenubar({ reportUuid: "", panel: <div>Hello</div> })
    await userEvent.type(screen.getByText(/Settings/), " ")
    expect(screen.getAllByText(/Hello/).length).toBe(1)
})

it("hides the view panel on click", async () => {
    renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/))
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    fireEvent.click(screen.getByText(/Settings/))
    await waitFor(() => expect(screen.queryAllByText(/Hello/).length).toBe(0))
})

it("hides the view panel on escape", async () => {
    renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/))
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await userEvent.keyboard("{Escape}")
    await waitFor(() => expect(screen.queryAllByText(/Hello/).length).toBe(0))
})
