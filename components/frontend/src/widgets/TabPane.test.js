import { render, screen } from "@testing-library/react"

import { DarkMode } from "../context/DarkMode"
import { Tab } from "../semantic_ui_react_wrappers"
import { tabPane } from "./TabPane"

it("shows the tab", () => {
    render(<Tab panes={[tabPane("Tab")]} />)
    expect(screen.queryAllByText("Tab").length).toBe(1)
})

it("is inverted in dark mode", () => {
    const { container } = render(
        <DarkMode.Provider value={true}>
            <Tab panes={[tabPane("Tab")]} />
        </DarkMode.Provider>,
    )
    expect(container.firstChild.firstChild.className).toEqual(expect.stringContaining("inverted"))
})

it("shows the tab red when there is an error", () => {
    render(<Tab panes={[tabPane("Tab", <p>Pane</p>, { error: true })]} />)
    expect(screen.getByText("Tab").className).toEqual(expect.stringContaining("red"))
})

it("shows the tab yellow when there is a warning", () => {
    render(<Tab panes={[tabPane("Tab", <p>Pane</p>, { warning: true })]} />)
    expect(screen.getByText("Tab").className).toEqual(expect.stringContaining("yellow"))
})

it("shows an icon", () => {
    const { container } = render(<Tab panes={[tabPane("Tab", <p>Pane</p>, { iconName: "server" })]} />)
    expect(container.firstChild.firstChild.firstChild.firstChild.className).toEqual(expect.stringContaining("server"))
})

it("shows an image", () => {
    const image = <img alt="" className="image" />
    const { container } = render(<Tab panes={[tabPane("Tab", <p>Pane</p>, { image: image })]} />)
    expect(container.firstChild.firstChild.firstChild.firstChild.className).toEqual(expect.stringContaining("image"))
})
