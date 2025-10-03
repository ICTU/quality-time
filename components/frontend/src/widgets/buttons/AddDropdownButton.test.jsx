import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { asyncClickRole, asyncClickText, expectNoText } from "../../testUtils"
import { AddDropdownButton } from "./AddDropdownButton"

function renderAddDropdownButton({ nrItems = 2, totalItems = 10, usedItemKeys = [], sort = true } = {}) {
    const mockCallback = vi.fn()
    const itemSubtypes = []
    let allItemSubtypes
    if (nrItems < totalItems) {
        allItemSubtypes = []
        for (const index of Array(totalItems).keys()) {
            const text = `Sub ${index + 1}`
            const key = text.toLowerCase()
            const option = { key: key, text: text, value: key, content: text }
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
    await asyncClickText(/Add foo/)
    expect(screen.getByLabelText(/Filter/)).toHaveFocus()
    await asyncClickText(/Sub 2/)
    expect(mockCallback).toHaveBeenCalledWith("sub 2")
})

test("AddDropdownButton keyboard navigation", async () => {
    const mockCallback = renderAddDropdownButton()
    await asyncClickText(/Add foo/)
    expect(screen.getByLabelText(/Filter/)).toHaveFocus()
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
    await asyncClickText(/Add foo/)
    expect(screen.getAllByText(/Sub/).map((item) => item.innerHTML)).toStrictEqual(["Sub 1", "Sub 2"])
})

test("AddDropdownButton is not sorted", async () => {
    renderAddDropdownButton({ sort: false })
    await asyncClickText(/Add foo/)
    expect(screen.getAllByText(/Sub/).map((item) => item.innerHTML)).toStrictEqual(["Sub 2", "Sub 1"])
})

test("AddDropdownButton filter one item", async () => {
    renderAddDropdownButton({ nrItems: 6 })
    await asyncClickText(/Add foo/)
    await userEvent.type(screen.getByRole("searchbox"), "Sub 3")
    expect(screen.getAllByText(/Sub/).map((item) => item.innerHTML)).toStrictEqual(["Sub 3"])
})

test("AddDropdownButton filter zero items", async () => {
    renderAddDropdownButton({ nrItems: 6 })
    await asyncClickText(/Add foo/)
    await userEvent.type(screen.getByRole("searchbox"), "FOO{Enter}")
    expectNoText(/Sub/)
})

test("AddDropdownButton select from all items", async () => {
    const mockCallback = renderAddDropdownButton()
    await asyncClickText(/Add foo/)
    await asyncClickRole("checkbox")
    await asyncClickText(/Sub 3/)
    expect(mockCallback).toHaveBeenCalledWith("sub 3")
})

test("AddDropdownButton hide used items", async () => {
    renderAddDropdownButton({ nrItems: 2, totalItems: 3, usedItemKeys: ["sub 1"] })
    await asyncClickText(/Add foo/)
    await asyncClickRole("checkbox", undefined, 1)
    expectNoText(/Sub 1/)
})

test("AddDropdownButton add all items by keyboard", async () => {
    const mockCallback = renderAddDropdownButton()
    await asyncClickText(/Add foo/)
    await userEvent.type(screen.getByRole("checkbox"), "{Enter}")
    await asyncClickText(/Sub 3/)
    expect(mockCallback).toHaveBeenCalledWith("sub 3")
})

test("AddDropdownButton menu can be closed without selecting an item", async () => {
    const mockCallback = renderAddDropdownButton()
    await asyncClickText(/Add foo/)
    await userEvent.keyboard("{Escape}")
    expectNoText(/Sub/)
    expect(mockCallback).not.toHaveBeenCalled()
})
