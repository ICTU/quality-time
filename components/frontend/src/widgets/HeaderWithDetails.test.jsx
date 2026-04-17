import { render } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { useSettings } from "../app_ui_settings"
import { clickText, expectSearch, expectText } from "../testUtils"
import { HeaderWithDetails } from "./HeaderWithDetails"

function HeaderWithDetailsWrapper({ header }) {
    const settings = useSettings()
    return (
        <HeaderWithDetails header={header} itemUuid="uuid" level="h1" settings={settings}>
            <p>Hello</p>
        </HeaderWithDetails>
    )
}

beforeEach(() => {
    history.push("")
})

it("expands the details on click", () => {
    render(<HeaderWithDetailsWrapper header="Expand" />)
    clickText("Expand")
    expectSearch("?expanded=uuid%3A0")
})

it("expands the details on space", async () => {
    render(<HeaderWithDetailsWrapper header="Header" />)
    await userEvent.tab()
    await userEvent.keyboard(" ")
    expectSearch("?expanded=uuid%3A0")
})

it("is expanded on load when listed in the query string", () => {
    history.push("?expanded=uuid:0")
    render(<HeaderWithDetailsWrapper header="Header" />)
    expectText("Hello")
})
