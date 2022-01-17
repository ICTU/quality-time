import React from 'react';
import { Icon, Menu, Popup } from 'semantic-ui-react';
import './HamburgerMenu.css';

export function ColumnMenuItem({ column, hiddenColumns, toggleHiddenColumn }) {
    return (
        <Menu.Item onClick={() => toggleHiddenColumn(column)}>
            {hiddenColumns.includes(column) ? `Show ${column} column` : `Hide ${column} column`}
        </Menu.Item>
    )
}

export function HamburgerMenu({ children }) {
    return (
        <Popup on={["click", "focus", "hover"]} hoverable position="bottom left" trigger={<Icon tabIndex="0" data-testid="HamburgerMenu" className="HamburgerMenu" name="sidebar"/>}>
            <Menu text vertical>
                {children}
            </Menu>
        </Popup>
    )
}
