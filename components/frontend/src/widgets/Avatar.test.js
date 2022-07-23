import React from 'react';
import { render, screen } from '@testing-library/react';
import { DarkMode } from '../context/DarkMode';
import { Avatar } from './Avatar';

it('shows the image when passed an email address', () => {
    render(<Avatar email="foo@bar" />)
    expect(screen.queryAllByAltText("Avatar").length).toBe(1)
    expect(screen.getByAltText("Avatar").getAttribute("src")).toEqual("https://www.gravatar.com/avatar/cca210311c3caf70e4a335aad6fa1047?d=identicon")
});

it('shows an icon when not passed an email address', () => {
    const { container} = render(<Avatar email="" />)
    expect(container.firstChild.className).toEqual("user icon")
});

it('is grey in dark mode', () => {
    const { container } = render(<DarkMode.Provider value={true}><Avatar email="" /></DarkMode.Provider>)
    expect(container.firstChild.className).toEqual(expect.stringContaining("grey"));
})
