import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { DarkMode } from '../context/DarkMode';
import { HyperLink } from './HyperLink';

it('shows the hyperlink', () => {
    render(<HyperLink url="https://url">Link</HyperLink>)
    expect(screen.queryAllByText("Link").length).toBe(1)
});

it('is grey in dark mode', () => {
    const { container } = render(<DarkMode.Provider value={true}><HyperLink url="https://url">Link</HyperLink></DarkMode.Provider>)
    expect(container.firstChild.className).toEqual(expect.stringContaining("inverted"));
})

it('is can be in error mode', () => {
    const { container } = render(<HyperLink url="https://url" error>Link</HyperLink>)
    expect(container.firstChild.className).toEqual(expect.stringContaining("error"));
})

it('does not propagate a click event', () => {
    const eventHandler = jest.fn()
    render(<div onClick={() => eventHandler()}><HyperLink url="https://url">Link</HyperLink></div>)
    fireEvent.click(screen.getByText(/Link/))
    expect(eventHandler).not.toBeCalled()
})
