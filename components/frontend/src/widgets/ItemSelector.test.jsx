import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { asyncClickRole, asyncClickText, expectNoText, expectText } from "../testUtils"
import { ItemSelector } from "./ItemSelector"

function renderItemSelector({
    nrItems = 2,
    totalItems = 10,
    usedItemKeysInReport = [],
    usedItemKeysInSubject = [],
    sort = true,
} = {}) {
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
        <ItemSelector
            allItemSubtypes={allItemSubtypes}
            itemType="foo"
            itemSubtypes={itemSubtypes.toReversed()} // Pass items in reversed order to test they are sorted correctly
            onClick={mockCallback}
            renderAnchor={(handleMenu) => (
                <button type="button" onClick={handleMenu}>
                    Add foo
                </button>
            )}
            tooltip="Add a new foo here"
            usedItemSubtypeKeysInReport={usedItemKeysInReport}
            usedItemSubtypeKeysInSubject={usedItemKeysInSubject}
            sort={sort}
        />,
    )
    return mockCallback
}

test("ItemSelector renders the child anchor", async () => {
    renderItemSelector()
    expectText(/Add foo/)
    expectNoText(/Available/) // Menu is closed until the anchor is clicked
})

test("ItemSelector mouse navigation", async () => {
    const mockCallback = renderItemSelector()
    await asyncClickText(/Add foo/)
    expect(screen.getByLabelText(/Filter/)).toHaveFocus()
    await asyncClickText(/Sub 2/)
    expect(mockCallback).toHaveBeenCalledWith("sub 2")
})

test("ItemSelector keyboard navigation", async () => {
    const mockCallback = renderItemSelector()
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

test("ItemSelector is sorted", async () => {
    renderItemSelector()
    await asyncClickText(/Add foo/)
    expect(screen.getAllByText(/Sub/).map((item) => item.innerHTML)).toStrictEqual(["Sub 1", "Sub 2"])
})

test("ItemSelector is not sorted", async () => {
    renderItemSelector({ sort: false })
    await asyncClickText(/Add foo/)
    expect(screen.getAllByText(/Sub/).map((item) => item.innerHTML)).toStrictEqual(["Sub 2", "Sub 1"])
})

test("ItemSelector filter one item", async () => {
    renderItemSelector({ nrItems: 6 })
    await asyncClickText(/Add foo/)
    await userEvent.type(screen.getByRole("searchbox"), "Sub 3")
    expect(screen.getAllByText(/Sub/).map((item) => item.innerHTML)).toStrictEqual(["Sub 3"])
})

test("ItemSelector filter zero items", async () => {
    renderItemSelector({ nrItems: 6 })
    await asyncClickText(/Add foo/)
    await userEvent.type(screen.getByRole("searchbox"), "FOO{Enter}")
    expectNoText(/Sub/)
})

test("ItemSelector select from all items", async () => {
    const mockCallback = renderItemSelector()
    await asyncClickText(/Add foo/)
    await asyncClickRole("checkbox")
    await asyncClickText(/Sub 3/)
    expect(mockCallback).toHaveBeenCalledWith("sub 3")
})

test("ItemSelector hide used items in report", async () => {
    renderItemSelector({
        nrItems: 2,
        totalItems: 3,
        usedItemKeysInReport: ["sub 1"],
    })
    await asyncClickText(/Add foo/)
    expectText(/Sub 1/)
    expectText(/Sub 2/)
    expectNoText(/Sub 3/) // Hidden because it's not supported by the subject type
    await asyncClickRole("checkbox", "Hide foo types already used in this:")
    await asyncClickRole("radio", "report")
    expectNoText(/Sub 1/) // Now hidden because it's already used in the report
    expectText(/Sub 2/)
    expectNoText(/Sub 3/) // Still hidden because it's not supported by the subject type
})

test("ItemSelector hide used items in subject", async () => {
    renderItemSelector({
        nrItems: 2,
        totalItems: 3,
        usedItemKeysInReport: ["sub 1", "sub 2"],
        usedItemKeysInSubject: ["sub 2"],
    })
    await asyncClickText(/Add foo/)
    expectText(/Sub 1/)
    expectText(/Sub 2/)
    expectNoText(/Sub 3/) // Hidden because it's not supported by the subject type
    await asyncClickRole("checkbox", "Hide foo types already used in this:")
    await asyncClickRole("radio", "subject")
    expectText(/Sub 1/)
    expectNoText(/Sub 2/) // Now hidden because it's already used in the subject
    expectNoText(/Sub 3/) // Still hidden because it's not supported by the subject type
})

test("ItemSelector add all items by keyboard", async () => {
    const mockCallback = renderItemSelector()
    await asyncClickText(/Add foo/)
    await userEvent.type(screen.getByRole("checkbox"), "{Enter}")
    await asyncClickText(/Sub 3/)
    expect(mockCallback).toHaveBeenCalledWith("sub 3")
})

test("ItemSelector menu can be closed without selecting an item", async () => {
    const mockCallback = renderItemSelector()
    await asyncClickText(/Add foo/)
    await userEvent.keyboard("{Escape}")
    expectNoText(/Sub/)
    expect(mockCallback).not.toHaveBeenCalled()
})
