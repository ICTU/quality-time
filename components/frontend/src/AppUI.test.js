import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { createMemoryHistory } from 'history';
import { datamodel, report } from "./__fixtures__/fixtures";
import { AppUI } from './AppUI';

it('shows an error message when there are no reports', () => {
    render(<AppUI history={{ location: { search: "" } }} report_uuid="" reports={[]} reports_overview={{}} />)
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it('handles sorting', async () => {
    const history = createMemoryHistory()
    render(<AppUI datamodel={datamodel} history={history} report_date={null} report_uuid="report_uuid" reports={[report]} reports_overview={{}} user="xxx" />)
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
    expect(history.location.search).toEqual("")
})

let matchMediaMatches
let changeMode

beforeAll(() => {
    Object.defineProperty(window, 'matchMedia', {
        value: jest.fn().mockImplementation(query => ({
            matches: matchMediaMatches,
            addEventListener: (eventType, eventHandler) => { changeMode = eventHandler },
            removeEventListener: () => { /* No implementation needed */ },
        }))
    });
});

it('supports dark mode', () => {
    matchMediaMatches = true
    const { container } = render(<AppUI history={{ location: { search: "" } }} report_uuid="" reports={[]} reports_overview={{}} />)
    expect(container.firstChild.style.background).toEqual("rgb(40, 40, 40)")
})

it('supports light mode', () => {
    matchMediaMatches = false
    const { container } = render(<AppUI history={{ location: { search: "" } }} report_uuid="" reports={[]} reports_overview={{}} />)
    expect(container.firstChild.style.background).toEqual("white")
})

it('follows OS mode when switching to light mode', () => {
    matchMediaMatches = true
    const { container } = render(<AppUI history={{ location: { search: "" }, replace: () => { /*  Dummy implementation */ } }} report_uuid="" reports={[]} reports_overview={{}} />)
    expect(container.firstChild.style.background).toEqual("rgb(40, 40, 40)")
    act(() => {
        changeMode({matches: false})
    })
    expect(container.firstChild.style.background).toEqual("white")
})

it('follows OS mode when switching to dark mode', () => {
    matchMediaMatches = false
    const { container } = render(<AppUI history={{ location: { search: "" }, replace: () => { /*  Dummy implementation */ } }} report_uuid="" reports={[]} reports_overview={{}} />)
    expect(container.firstChild.style.background).toEqual("white")
    act(() => {
        changeMode({matches: true})
    })
    expect(container.firstChild.style.background).toEqual("rgb(40, 40, 40)")
})

it('ignores OS mode when mode explicitly set', () => {
    matchMediaMatches = false
    const { container } = render(<AppUI history={{ location: { search: "?ui_mode=light" }, replace: () => { /*  Dummy implementation */ } }} report_uuid="" reports={[]} reports_overview={{}} />)
    expect(container.firstChild.style.background).toEqual("white")
    act(() => {
        changeMode({matches: true})
    })
    expect(container.firstChild.style.background).toEqual("white")
})
