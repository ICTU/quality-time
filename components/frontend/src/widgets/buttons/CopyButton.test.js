import { act, fireEvent, render, screen } from "@testing-library/react"

import { CopyButton } from "./CopyButton"

Array("report", "subject", "metric", "source").forEach((itemType) => {
    test("CopyButton has the correct label", () => {
        render(<CopyButton itemType={itemType} />)
        expect(screen.getAllByText(new RegExp(`Copy ${itemType}`)).length).toBe(1)
    })

    test("CopyButton can be used to select an item", async () => {
        const mockCallback = jest.fn()
        render(
            <CopyButton
                itemType={itemType}
                onChange={mockCallback}
                get_options={() => {
                    return [{ key: "1", text: "Item", value: "1" }]
                }}
            />,
        )
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Copy ${itemType}`)))
        })
        await act(async () => {
            fireEvent.click(screen.getByText(/Item/))
        })
        expect(mockCallback).toHaveBeenCalledWith("1")
    })

    test("CopyButton loads the options every time the menu is opened", async () => {
        const mockCallback = jest.fn()
        let get_options_called = 0
        render(
            <CopyButton
                itemType={itemType}
                onChange={mockCallback}
                get_options={() => {
                    get_options_called++
                    return [{ key: "1", text: "Item", value: "1" }]
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
        expect(get_options_called).toBe(2)
    })
})
