import React from 'react';
import { Dropdown } from 'semantic-ui-react';
import './HamburgerMenu.css';

export function ColumnMenuItem({ column, hiddenColumns, toggleHiddenColumn }) {
    return (
        <Dropdown.Item onClick={() => toggleHiddenColumn(column)}>
            {hiddenColumns.includes(column) ? `Show ${column} column` : `Hide ${column} column`}
        </Dropdown.Item>
    )
}

export function HamburgerMenu({ children }) {
    return (
        <Dropdown className="HamburgerMenu" item icon='sidebar' simple>
            <Dropdown.Menu>
                {children}
            </Dropdown.Menu>
        </Dropdown>
    )
}
