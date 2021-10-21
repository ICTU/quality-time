import React from 'react';
import { Dropdown } from 'semantic-ui-react';
import './HamburgerMenu.css';

export function HamburgerMenu({ children }) {
    return (
        <Dropdown className="HamburgerMenu" item simple icon='sidebar'>
            <Dropdown.Menu>
                {children}
            </Dropdown.Menu>
        </Dropdown>
    )
}
