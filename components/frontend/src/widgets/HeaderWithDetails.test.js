import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { HeaderWithDetails } from "./HeaderWithDetails"

beforeEach(() => {
    history.push("")
})

it("expands the details on click", () => {
    render(
        <HeaderWithDetails item_uuid="uuid" level="h1" settings={createTestableSettings()} header="Expand">
            <p>Hello</p>
        </HeaderWithDetails>,
    )
    fireEvent.click(screen.getByText("Expand"))
    expect(history.location.search).toBe("?expanded=uuid")
})

it("expands the details on space", async () => {
    render(
        <HeaderWithDetails header="Header" item_uuid="uuid" level="h1" settings={createTestableSettings()}>
            <p>Hello</p>
        </HeaderWithDetails>,
    )
    await userEvent.tab()
    await userEvent.keyboard(" ")
    expect(history.location.search).toBe("?expanded=uuid")
})

it("is expanded on load when listed in the query string", () => {
    history.push("?expanded=uuid")
    render(
        <HeaderWithDetails header="Header" item_uuid="uuid" level="h1" settings={createTestableSettings()}>
            <p>Hello</p>
        </HeaderWithDetails>,
    )
    expect(screen.getAllByText("Hello").length).toBe(1)
})
