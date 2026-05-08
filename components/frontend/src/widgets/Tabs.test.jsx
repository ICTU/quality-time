import { render } from "@testing-library/react"
import history from "history/browser"

import { useSettings } from "../app_ui_settings"
import { clickText, expectSearch, expectText } from "../testUtils"
import { Tabs } from "./Tabs"

function TabsWrapper() {
    const settings = useSettings()
    return (
        <Tabs settings={settings} tabs={[{ label: "First" }, { label: "Second" }]} uuid="uuid">
            <p>First panel</p>
            <p>Second panel</p>
        </Tabs>
    )
}

beforeEach(() => history.push(""))

it("shows the first tab panel by default", () => {
    render(<TabsWrapper />)
    expectText("First panel")
})

it("switches to another tab on click", () => {
    render(<TabsWrapper />)
    clickText("Second")
    expectSearch("?expanded=uuid%3A1")
    expectText("Second panel")
})
