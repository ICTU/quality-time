import React from 'react';
import { Dropdown } from 'semantic-ui-react';
import './HamburgerMenu.css';

export function HamburgerMenu({ children }) {
    return (
        <Dropdown className="HamburgerMenu" openOnFocus={false} item icon='sidebar'>
            <Dropdown.Menu>
                {children}
            </Dropdown.Menu>
        </Dropdown>
    )
}
