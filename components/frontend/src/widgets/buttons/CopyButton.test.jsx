import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { CopyButton } from "./CopyButton"

function renderCopyButton(itemType, mockCallback) {
    render(
        <CopyButton
            itemType={itemType}
            onChange={mockCallback}
            get_options={() => {
                return [{ key: "1", text: "Item", value: "1", content: "Item" }]
            }}
        />,
    )
}

Array("report", "subject", "metric", "source").forEach((itemType) => {
    test("CopyButton has the correct label", () => {
        render(<CopyButton itemType={itemType} get_options={() => []} />)
        expect(screen.getAllByText(new RegExp(`Copy ${itemType}`)).length).toBe(1)
    })

    test("CopyButton can be used to select an item", async () => {
        const mockCallback = vi.fn()
        renderCopyButton(itemType, mockCallback)
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Copy ${itemType}`)))
        })
        await act(async () => {
            fireEvent.click(screen.getByText(/Item/))
        })
        expect(mockCallback).toHaveBeenCalledWith("1")
    })

    test("CopyButton menu can be closed without selecting an item", async () => {
        const mockCallback = vi.fn()
        renderCopyButton(itemType, mockCallback)
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Copy ${itemType}`)))
        })
        await userEvent.keyboard("{Escape}")
        expect(screen.queryAllByText(/Item/).length).toBe(0)
        expect(mockCallback).not.toHaveBeenCalled()
    })

    test("CopyButton loads the options every time the menu is opened", async () => {
        const mockCallback = vi.fn()
        let get_options_called = 0
        render(
            <CopyButton
                itemType={itemType}
                onChange={mockCallback}
                get_options={() => {
                    get_options_called++
                    return [{ key: "1", text: "Item", value: "1", content: "Item" }]
                }}
            />,
        )
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Copy ${itemType}`)))
        })
        fireEvent.click(screen.getByText(/Item/))
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Copy ${itemType}`)))
        })
        expect(get_options_called).toBe(4)
    })
})
