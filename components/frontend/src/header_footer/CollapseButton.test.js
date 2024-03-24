import { fireEvent, render, renderHook, screen } from "@testing-library/react"
import history from "history/browser"
import { CollapseButton } from "./CollapseButton"
import { useExpandedItemsSearchQuery } from "../app_ui_settings"
import { createTestableSettings } from "../__fixtures__/fixtures"

beforeEach(() => {
    history.push("")
})

function renderCollapseButton({ expandedItems = null } = {}) {
    const settings = createTestableSettings()
    render(<CollapseButton expandedItems={expandedItems ?? settings.expandedItems} />)
}

it("resets the expanded items", () => {
    history.push("?expanded=tab")
    const expandedItems = renderHook(() => useExpandedItemsSearchQuery())
    expect(expandedItems.result.current.value).toStrictEqual(["tab"])
    renderCollapseButton({ expandedItems: expandedItems.result.current })
    fireEvent.click(screen.getByRole("button", { name: "Collapse all headers and metrics" }))
    expandedItems.rerender()
    expect(expandedItems.result.current.value).toStrictEqual([])
})

it("doesn't change the expanded items if there are none", () => {
    const expandedItems = renderHook(() => useExpandedItemsSearchQuery())
    expect(expandedItems.result.current.value).toStrictEqual([])
    renderCollapseButton({ expandedItems: expandedItems.result.current })
    fireEvent.click(screen.getByRole("button", { name: "Collapse all headers and metrics" }))
    expandedItems.rerender()
    expect(expandedItems.result.current.value).toStrictEqual([])
})
