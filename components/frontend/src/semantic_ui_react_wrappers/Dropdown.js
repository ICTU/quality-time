import React, { useContext } from 'react';
import { Dropdown as SemanticUIDropdown } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import { addInvertedClassNameWhenInDarkMode } from './dark_mode';

export function Dropdown(props) {
    return (
        <SemanticUIDropdown {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
    )
}

Dropdown.Divider = SemanticUIDropdown.Divider
Dropdown.Header = SemanticUIDropdown.Header
Dropdown.Item = SemanticUIDropdown.Item
Dropdown.Menu = SemanticUIDropdown.Menu
Dropdown.SearchInput = SemanticUIDropdown.SearchInput
Dropdown.Text = SemanticUIDropdown.Text
