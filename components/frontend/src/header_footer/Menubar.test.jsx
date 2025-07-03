import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { expectNoAccessibilityViolations } from "../testUtils"
import { Menubar } from "./Menubar"

beforeEach(() => history.push(""))

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
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Menubar
                onDate={vi.fn()}
                openReportsOverview={openReportsOverview}
                panel={panel}
                reportUuid={reportUuid}
                settings={settings}
                setUser={setUser}
                user={user}
            />
        </LocalizationProvider>,
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
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({
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
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: false })
    const setUser = vi.fn()
    const { container } = renderMenubar({ setUser: setUser })
    await enterCredentials(container)
    expect(screen.getAllByText(/Invalid credentials/).length).toBe(1)
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith("post", "login", CREDENTIALS)
    expect(setUser).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("shows connection error message", async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockRejectedValue(new Error("Async error message"))
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
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
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

it("shows and hides the settings panel on button click", async () => {
    const { container } = renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/))
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
    fireEvent.click(screen.getByText(/Settings/))
    await waitFor(() => expect(screen.queryAllByText(/Hello/).length).toBe(0))
})

it("shows and hides the settings panel on keypress", async () => {
    renderMenubar({ reportUuid: "", panel: <div>Hello</div> })
    await userEvent.type(screen.getByText(/Settings/), " ")
    expect(screen.getAllByText(/Hello/).length).toBe(1)
    await userEvent.type(screen.getByText(/Hello/), "{Escape}")
    await waitFor(() => expect(screen.queryAllByText(/Hello/).length).toBe(0))
})

it("shows and hides the report period panel on button click", async () => {
    const { container } = renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/today/))
    expect(screen.getAllByText(/Report date/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
    fireEvent.click(screen.getByText(/today/))
    await waitFor(() => expect(screen.queryAllByText(/Report date/).length).toBe(0))
})

it("switches from settings to report period panel", async () => {
    const { container } = renderMenubar({ panel: <div>Hello</div> })
    fireEvent.click(screen.getByText(/Settings/))
    fireEvent.click(screen.getByText(/today/))
    expect(screen.queryAllByText(/Hello/).length).toBe(0)
    expect(screen.getAllByText(/Report date/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})
