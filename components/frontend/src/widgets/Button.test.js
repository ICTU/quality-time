import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import {
    AddButton,
    AddDropdownButton,
    CopyButton,
    DeleteButton,
    MoveButton,
    PermLinkButton,
    ReorderButtonGroup,
} from "./Button"
import * as toast from "./toast"

function renderAddDropdownButton(nrItems = 2, totalItems = 10, usedItemKeys = []) {
    const mockCallback = jest.fn()
    const itemSubtypes = []
    let allItemSubtypes
    if (nrItems < totalItems) {
        allItemSubtypes = []
        for (const index of Array(totalItems).keys()) {
            const text = `Sub ${index + 1}`
            const key = text.toLowerCase()
            const option = { key: key, text: text, value: key }
            allItemSubtypes.push(option)
            if (index < nrItems) {
                itemSubtypes.push(option)
            }
        }
    }
    render(
        <AddDropdownButton
            allItemSubtypes={allItemSubtypes}
            itemType="foo"
            itemSubtypes={itemSubtypes}
            onClick={mockCallback}
            usedItemSubtypeKeys={usedItemKeys}
        />,
    )
    return mockCallback
}

test("AddDropdownButton mouse navigation", async () => {
    const mockCallback = renderAddDropdownButton()
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await act(async () => {
        fireEvent.click(screen.getByText(/Sub 2/))
    })
    expect(mockCallback).toHaveBeenCalledWith("sub 2")
})

test("AddDropdownButton keyboard navigation", async () => {
    const mockCallback = renderAddDropdownButton()
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await act(async () => {
        fireEvent.keyDown(screen.getByText(/Available/), { key: "ArrowDown" })
    })
    await act(async () => {
        fireEvent.keyDown(screen.getByText(/Available/), { key: "ArrowUp" })
    })
    await act(async () => {
        fireEvent.keyDown(screen.getByText(/Available/), { key: "ArrowDown" })
    })
    await act(async () => {
        fireEvent.keyDown(screen.getByText(/Sub 2/), { key: "Enter" })
    })
    expect(mockCallback).toHaveBeenCalledWith("sub 2")
})

test("AddDropdownButton hides popup when dropdown is shown", async () => {
    renderAddDropdownButton()
    await userEvent.hover(screen.getByText(/Add foo/))
    await waitFor(() => {
        expect(screen.queryAllByText(/Add a new foo here/).length).toBe(1)
    })
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    expect(screen.queryAllByText(/Add a new foo here/).length).toBe(0) // Popup should disappear
    await userEvent.type(screen.getByText(/Add foo/), "{Escape}") // Close dropdown
    await userEvent.hover(screen.getByText(/Add foo/))
    await waitFor(() => {
        expect(screen.queryAllByText(/Add a new foo here/).length).toBe(1)
    }) // Popup should appear again
})

test("AddDropdownButton filter one item", async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub 6{Enter}")
    expect(mockCallback).toHaveBeenCalledWith("sub 6")
})

test("AddDropdownButton filter one item without focus", async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    const dropdown = screen.getByText(/Add foo/)
    await act(async () => {
        fireEvent.keyDown(dropdown, { key: "9" })
    })
    await act(async () => {
        fireEvent.keyDown(dropdown, { key: "Backspace" })
    })
    await act(async () => {
        fireEvent.keyDown(dropdown, { key: "6" })
    })
    await act(async () => {
        fireEvent.keyDown(dropdown, { key: "Enter" })
    })
    expect(mockCallback).toHaveBeenCalledWith("sub 6")
})

test("AddDropdownButton filter zero items", async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "FOO{Enter}")
    expect(mockCallback).not.toHaveBeenCalled()
})

test("AddDropdownButton add all items", async () => {
    const mockCallback = renderAddDropdownButton()
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await act(async () => {
        fireEvent.click(screen.getByRole("checkbox"))
    })
    await act(async () => {
        fireEvent.click(screen.getByText(/Sub 3/))
    })
    expect(mockCallback).toHaveBeenCalledWith("sub 3")
})

test("AddDropdownButton hide used items", async () => {
    renderAddDropdownButton(2, 3, ["sub 1"])
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await act(async () => {
        fireEvent.click(screen.getAllByRole("checkbox")[1])
    })
    expect(screen.queryAllByText(/Sub 1/).length).toBe(0)
})

test("AddDropdownButton add all items by keyboard", async () => {
    const mockCallback = renderAddDropdownButton()
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByRole("checkbox"), " ")
    // Somehow the space does not trigger the checkbox, so hit Enter as well
    await userEvent.type(screen.getByRole("checkbox"), "{Enter}")
    await act(async () => {
        fireEvent.click(screen.getByText(/Sub 3/))
    })
    expect(mockCallback).toHaveBeenCalledWith("sub 3")
})

test("AddDropdownButton resets query on escape", async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "FOO{Escape}")
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await act(async () => {
        fireEvent.keyDown(screen.getByText(/Sub 1/), { key: "Enter" })
    })
    expect(mockCallback).toHaveBeenCalledWith("sub 1")
})

test("AddDropdownButton does not reset query on blur when it has checkbox", async () => {
    renderAddDropdownButton()
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub 3{Tab}")
    expect(screen.queryAllByText(/Sub 1/).length).toBe(0)
})

test("AddDropdownButton does reset query on blur when it has no checkbox", async () => {
    renderAddDropdownButton(10)
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub 3{Tab}")
    expect(screen.queryAllByText(/Sub 3/).length).toBe(0)
})

test("AddDropdownButton does not add selected item on enter when menu is closed", async () => {
    const mockCallback = renderAddDropdownButton(6)
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub{Escape}")
    await act(async () => {
        fireEvent.keyDown(screen.getByText(/Add foo/), { key: "Enter" })
    })
    expect(mockCallback).not.toHaveBeenCalled()
})

test("AddButton has the correct label", () => {
    render(<AddButton itemType="bar" />)
    expect(screen.getAllByText(/bar/).length).toBe(1)
})

test("DeleteButton has the correct label", () => {
    render(<DeleteButton itemType="bar" />)
    expect(screen.getAllByText(/bar/).length).toBe(1)
})

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

    test("MoveButton has the correct label", () => {
        render(<MoveButton itemType={itemType} />)
        expect(screen.getAllByText(new RegExp(`Move ${itemType}`)).length).toBe(1)
    })

    test("MoveButton can be used to select an item", async () => {
        const mockCallback = jest.fn()
        render(
            <MoveButton
                itemType={itemType}
                onChange={mockCallback}
                get_options={() => {
                    return [{ key: "1", text: "Item", value: "1" }]
                }}
            />,
        )
        await act(async () => {
            fireEvent.click(screen.getByText(new RegExp(`Move ${itemType}`)))
        })
        await act(async () => {
            fireEvent.click(screen.getByText(/Item/))
        })
        expect(mockCallback).toHaveBeenCalledWith("1")
    })
})

Array("first", "last", "previous", "next").forEach((direction) => {
    test("ReorderButtonGroup calls the callback on click direction", async () => {
        const mockCallback = jest.fn()
        render(<ReorderButtonGroup onClick={mockCallback} moveable="item" />)
        await act(async () => {
            fireEvent.click(screen.getByLabelText(`Move item to the ${direction} position`))
        })
        expect(mockCallback).toHaveBeenCalledWith(direction)
    })

    test("ReorderButtonGroup does not call the callback on click direction when the button group is already there", () => {
        const mockCallback = jest.fn()
        render(<ReorderButtonGroup onClick={mockCallback} first={true} last={true} moveable="item" />)
        fireEvent.click(screen.getByLabelText(`Move item to the ${direction} position`))
        expect(mockCallback).not.toHaveBeenCalled()
    })
})

test("PermLinkButton is not shown in an insecure context", () => {
    Object.assign(window, { isSecureContext: false })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    expect(screen.queryAllByText(/Share/).length).toBe(0)
})

test("PermLinkButton copies URL to clipboard", async () => {
    toast.showMessage = jest.fn()
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: { writeText: jest.fn().mockImplementation(() => Promise.resolve()) },
    })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    await act(async () => {
        fireEvent.click(screen.getByText(/Share/))
    })
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith("https://example.org")
    expect(toast.showMessage).toHaveBeenCalledWith("success", "Copied URL to clipboard")
})

test("PermLinkButton shows error message if copying fails", async () => {
    toast.showMessage = jest.fn()
    Object.assign(window, { isSecureContext: true })
    Object.assign(navigator, {
        clipboard: {
            writeText: jest.fn().mockImplementation(() => Promise.reject(new Error("fail"))),
        },
    })
    render(<PermLinkButton itemType="metric" url="https://example.org" />)
    await act(async () => {
        fireEvent.click(screen.getByText(/Share/))
    })
    expect(toast.showMessage).toHaveBeenCalledWith("error", "Could not copy URL to clipboard", "Error: fail")
})
