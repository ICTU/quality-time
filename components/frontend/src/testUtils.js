import { act, fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { axe } from "jest-axe"
import { vi } from "vitest"

import * as fetchServerApi from "./api/fetch_server_api"

export async function expectNoAccessibilityViolations(container) {
    vi.useRealTimers()
    await act(async () => expect(await axe(container)).toHaveNoViolations())
}

export function expectFetch() {
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith(...arguments)
}

export function expectNoFetch() {
    expect(fetchServerApi.fetchServerApi).not.toHaveBeenCalled()
}

export function expectSearch(query) {
    expect(history.location.search).toBe(query)
}

export function expectText(text, count = 1) {
    expect(screen.getAllByText(text).length).toBe(count)
}

export async function expectTextAfterWait(text) {
    await waitFor(() => {
        expectText(text)
    })
}
export function expectNoText(text) {
    expect(screen.queryAllByText(text).length).toBe(0)
}

export async function expectNoTextAfterWait(text) {
    await waitFor(() => {
        expectNoText(text)
    })
}

export function expectLabelText(text, count = 1) {
    expect(screen.getAllByLabelText(text).length).toBe(count)
}

export function expectNoLabelText(text) {
    expect(screen.queryAllByLabelText(text).length).toBe(0)
}

export function clickText(text, index) {
    // Click the element containing the text. Returns the element.
    // If index is provided, assume multiple elements match and click the element with the given index
    const element = index === undefined ? screen.getByText(text) : screen.getAllByText(text)[index]
    fireEvent.click(element)
    return element
}

export async function asyncClickText(text, index) {
    // Asynchronously click the element containing the text. Returns the element.
    // If index is provided, assume multiple elements match and click the element with the given index
    await act(async () => {
        return clickText(text, index)
    })
}

export function clickRole(role, name, index) {
    // Click the element with the given role and the given name. Returns the element.
    // If index is provided, assume multiple elements match and click the element with the given index
    const options = name ? { name: name } : undefined
    const element = index === undefined ? screen.getByRole(role, options) : screen.getAllByRole(role, options)[index]
    fireEvent.click(element)
    return element
}

export async function asyncClickRole(role, name, index) {
    // Asynchronously click the element with the given role and the given name. Returns the element.
    // If index is provided, assume multiple elements match and click the element with the given index
    await act(async () => {
        return clickRole(role, name, index)
    })
}

export function clickButton(name, index) {
    // Click the element with the role button and the given name. Returns the button.
    // If index is provided, assume multiple buttons match and click the button with the given index
    return clickRole("button", name, index)
}

export async function asyncClickButton(name, index) {
    // Asynchronously click the element with the role button and the given name. Returns the button.
    // If index is provided, assume multiple buttons match and click the button with the given index
    await act(async () => {
        return clickButton(name, index)
    })
}

export function clickMenuItem(name, index) {
    // Click the element with the role menuitem and the given name. Returns the menuitem.
    // If index is provided, assume multiple menuitems match and click the menuitem with the given index
    return clickRole("menuitem", name, index)
}

export async function asyncClickMenuItem(name, index) {
    // Asynchronously click the element with the role menuitem and the given name. Returns the menuitem.
    // If index is provided, assume multiple menuitems match and click the menuitem with the given index
    await act(async () => {
        return clickRole("menuitem", name, index)
    })
}

export function clickLabeledElement(text, index) {
    // Click the element labeled with the text. Returns the element.
    // If index is provided, assume multiple elements match and click the element with the given index
    const element = index === undefined ? screen.getByLabelText(text) : screen.getAllByLabelText(text)[index]
    fireEvent.click(element)
    return element
}

export async function asyncClickLabeledElement(text, index) {
    // Asynchronously click the element labeled with the text. Returns the element.
    // If index is provided, assume multiple elements match and click the element with the given index
    await act(async () => {
        return clickLabeledElement(text, index)
    })
}

export async function hoverText(text) {
    await userEvent.hover(screen.queryByText(text))
}
