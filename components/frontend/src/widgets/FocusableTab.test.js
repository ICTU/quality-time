import React from 'react';
import { render, screen } from '@testing-library/react';
import { DarkMode } from '../context/DarkMode';
import { FocusableTab } from './FocusableTab';

it('shows the tab', () => {
    render(<FocusableTab>Tab</FocusableTab>)
    expect(screen.queryAllByText("Tab").length).toBe(1)
});

it('is inverted in dark mode', () => {
    const { container } = render(<DarkMode.Provider value={true}><FocusableTab>Tab</FocusableTab></DarkMode.Provider>)
    expect(container.firstChild.className).toEqual(expect.stringContaining("inverted"));
})
