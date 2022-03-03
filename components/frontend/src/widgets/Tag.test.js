import React from 'react';
import { render } from '@testing-library/react';
import { DarkMode } from '../context/DarkMode';
import { Tag } from './Tag';

it('is grey in dark mode', () => {
    const { container } = render(<DarkMode.Provider value={true}><Tag tag="tag" /></DarkMode.Provider>)
    expect(container.firstChild.className).toEqual(expect.stringContaining("grey"));
})

it('is not grey in light mode', () => {
    const { container } = render(<DarkMode.Provider value={false}><Tag tag="tag" /></DarkMode.Provider>)
    expect(container.firstChild.className).toEqual(expect.not.stringContaining("grey"));
})

it('is blue when selected in dark mode', () => {
    const { container } = render(<DarkMode.Provider value={true}><Tag selected tag="tag" /></DarkMode.Provider>)
    expect(container.firstChild.className).toEqual(expect.stringContaining("blue"));
})

it('is blue when selected in light mode', () => {
    const { container } = render(<DarkMode.Provider value={false}><Tag selected tag="tag" /></DarkMode.Provider>)
    expect(container.firstChild.className).toEqual(expect.stringContaining("blue"));
})
