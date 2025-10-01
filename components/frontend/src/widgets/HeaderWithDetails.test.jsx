import { render } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { clickText, expectSearch, expectText } from "../testUtils"
import { HeaderWithDetails } from "./HeaderWithDetails"

beforeEach(() => {
    history.push("")
})

it("expands the details on click", () => {
    render(
        <HeaderWithDetails itemUuid="uuid" level="h1" settings={createTestableSettings()} header="Expand">
            <p>Hello</p>
        </HeaderWithDetails>,
    )
    clickText("Expand")
    expectSearch("?expanded=uuid%3A0")
})

it("expands the details on space", async () => {
    render(
        <HeaderWithDetails header="Header" itemUuid="uuid" level="h1" settings={createTestableSettings()}>
            <p>Hello</p>
        </HeaderWithDetails>,
    )
    await userEvent.tab()
    await userEvent.keyboard(" ")
    expectSearch("?expanded=uuid%3A0")
})

it("is expanded on load when listed in the query string", () => {
    history.push("?expanded=uuid:0")
    render(
        <HeaderWithDetails header="Header" itemUuid="uuid" level="h1" settings={createTestableSettings()}>
            <p>Hello</p>
        </HeaderWithDetails>,
    )
    expectText("Hello")
})
