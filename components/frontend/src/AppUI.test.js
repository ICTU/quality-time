import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import history from 'history/browser';
import { datamodel, report } from "./__fixtures__/fixtures";
import { AppUI } from './AppUI';
import * as fetch_server_api from './api/fetch_server_api';
import { mockGetAnimations } from './dashboard/MockAnimations';

beforeEach(() => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) });
    mockGetAnimations()
});

afterEach(() => jest.restoreAllMocks())

it('shows an error message when there are no reports', async () => {
    await act(async () => render(<AppUI report_uuid="" reports={[]} reports_overview={{}} />))
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it('handles sorting', async () => {
    await act(async () => render(<AppUI datamodel={datamodel} report_date={null} report_uuid="report_uuid" reports={[report]} reports_overview={{}} user="xxx" />))
    fireEvent.click(screen.getAllByText("Comment")[0])
    expect(history.location.search).toEqual("?sort_column=comment")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("?sort_column=status")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("?sort_column=status&sort_direction=descending")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("")
    fireEvent.click(screen.getAllByText("Comment")[0])
    expect(history.location.search).toEqual("?sort_column=comment")
    await act(async () => fireEvent.click(screen.getAllByText(/Add metric/)[0]))
    await act(async () => fireEvent.click(screen.getAllByText(/Metric type/)[0]))
    expect(history.location.search).toEqual("")
})

let matchMediaMatches
let changeMode

beforeAll(() => {
    Object.defineProperty(window, 'matchMedia', {
        value: jest.fn().mockImplementation(_query => ({
            matches: matchMediaMatches,
            addEventListener: (_eventType, eventHandler) => { changeMode = eventHandler },
            removeEventListener: () => { /* No implementation needed */ },
        }))
    });
});

beforeEach(() => {
    history.push("")
})

async function renderAppUI() {
    return await act(async () => render(<AppUI report_uuid="" reports={[]} reports_overview={{}} />))
}

it('supports dark mode', async () => {
    matchMediaMatches = true
    const { container } = await renderAppUI()
    expect(container.firstChild.style.background).toEqual("rgb(40, 40, 40)")
})

it('supports light mode', async () => {
    matchMediaMatches = false
    const { container } = await renderAppUI()
    expect(container.firstChild.style.background).toEqual("white")
})

it('follows OS mode when switching to light mode', async () => {
    matchMediaMatches = true
    const { container } = await renderAppUI()
    expect(container.firstChild.style.background).toEqual("rgb(40, 40, 40)")
    act(() => {
        changeMode({matches: false})
    })
    expect(container.firstChild.style.background).toEqual("white")
})

it('follows OS mode when switching to dark mode', async () => {
    matchMediaMatches = false
    const { container } = await renderAppUI()
    expect(container.firstChild.style.background).toEqual("white")
    act(() => {
        changeMode({matches: true})
    })
    expect(container.firstChild.style.background).toEqual("rgb(40, 40, 40)")
})

it('ignores OS mode when mode explicitly set', async () => {
    matchMediaMatches = false
    history.push("?ui_mode=light")
    const { container } = await renderAppUI()
    expect(container.firstChild.style.background).toEqual("white")
    act(() => {
        changeMode({matches: true})
    })
    expect(container.firstChild.style.background).toEqual("white")
})
