import { render } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { asyncClickText, clickText, expectNoText, expectText } from "../../testUtils"
import { CopyButton } from "./CopyButton"

function renderCopyButton(itemType, mockCallback) {
    render(
        <CopyButton
            itemType={itemType}
            onChange={mockCallback}
            getOptions={() => {
                return [{ key: "1", text: "Item", value: "1", content: "Item" }]
            }}
        />,
    )
}

Array("report", "subject", "metric", "source").forEach((itemType) => {
    test("CopyButton has the correct label", () => {
        render(<CopyButton itemType={itemType} getOptions={() => []} />)
        expectText(new RegExp(`Copy ${itemType}`))
    })

    test("CopyButton can be used to select an item", async () => {
        const mockCallback = vi.fn()
        renderCopyButton(itemType, mockCallback)
        await asyncClickText(new RegExp(`Copy ${itemType}`))
        await asyncClickText(/Item/)
        expect(mockCallback).toHaveBeenCalledWith("1")
    })

    test("CopyButton menu can be closed without selecting an item", async () => {
        const mockCallback = vi.fn()
        renderCopyButton(itemType, mockCallback)
        await asyncClickText(new RegExp(`Copy ${itemType}`))
        await userEvent.keyboard("{Escape}")
        expectNoText(/Item/)
        expect(mockCallback).not.toHaveBeenCalled()
    })

    test("CopyButton loads the options every time the menu is opened", async () => {
        const mockCallback = vi.fn()
        let getOptionsCalled = 0
        render(
            <CopyButton
                itemType={itemType}
                onChange={mockCallback}
                getOptions={() => {
                    getOptionsCalled++
                    return [{ key: "1", text: "Item", value: "1", content: "Item" }]
                }}
            />,
        )
        await asyncClickText(new RegExp(`Copy ${itemType}`))
        clickText(/Item/)
        await asyncClickText(new RegExp(`Copy ${itemType}`))
        expect(getOptionsCalled).toBe(4)
    })
})
