import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AddDropdownButton } from "./AddDropdownButton"

function renderAddDropdownButton({ nrItems = 2, totalItems = 10, usedItemKeys = [], sort = true } = {}) {
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
            itemSubtypes={itemSubtypes.toReversed()} // Pass items in reversed order to test they are sorted correctly
            onClick={mockCallback}
            usedItemSubtypeKeys={usedItemKeys}
            sort={sort}
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

test("AddDropdownButton is sorted", async () => {
    renderAddDropdownButton()
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    expect(screen.getAllByText(/Sub/).map((item) => item.innerHTML)).toStrictEqual(["Sub 1", "Sub 2"])
})

test("AddDropdownButton is not sorted", async () => {
    renderAddDropdownButton({ sort: false })
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    expect(screen.getAllByText(/Sub/).map((item) => item.innerHTML)).toStrictEqual(["Sub 2", "Sub 1"])
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
    const mockCallback = renderAddDropdownButton({ nrItems: 6 })
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub 6{Enter}")
    expect(mockCallback).toHaveBeenCalledWith("sub 6")
})

test("AddDropdownButton filter one item without focus", async () => {
    const mockCallback = renderAddDropdownButton({ nrItems: 6 })
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
    const mockCallback = renderAddDropdownButton({ nrItems: 6 })
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
    renderAddDropdownButton({ nrItems: 2, totalItems: 3, usedItemKeys: ["sub 1"] })
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
    const mockCallback = renderAddDropdownButton({ nrItems: 6 })
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
    renderAddDropdownButton({ nrItems: 10 })
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub 3{Tab}")
    expect(screen.queryAllByText(/Sub 3/).length).toBe(0)
})

test("AddDropdownButton does not add selected item on enter when menu is closed", async () => {
    const mockCallback = renderAddDropdownButton({ nrItems: 6 })
    await act(async () => {
        fireEvent.click(screen.getByText(/Add foo/))
    })
    await userEvent.type(screen.getByPlaceholderText(/Filter/), "Sub{Escape}")
    await act(async () => {
        fireEvent.keyDown(screen.getByText(/Add foo/), { key: "Enter" })
    })
    expect(mockCallback).not.toHaveBeenCalled()
})
