import React, { useContext } from 'react';
import { Dropdown as SemanticUIDropdown } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Dropdown(props) {
    let { className, ...otherProps } = props
    if (useContext(DarkMode)) {
        className += " inverted"
    }
    return (
        <SemanticUIDropdown className={className} {...otherProps} />
    )
}

Dropdown.Divider = SemanticUIDropdown.Divider
Dropdown.Header = SemanticUIDropdown.Header
Dropdown.Item = SemanticUIDropdown.Item
Dropdown.Menu = SemanticUIDropdown.Menu
Dropdown.SearchInput = SemanticUIDropdown.SearchInput
Dropdown.Text = SemanticUIDropdown.Text
