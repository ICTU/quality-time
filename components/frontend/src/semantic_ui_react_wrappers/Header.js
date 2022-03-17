import React, { useContext } from 'react';
import { Header as SemanticUIHeader } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import './Header.css';

export function Header(props) {
    return (
        <SemanticUIHeader inverted={useContext(DarkMode)} {...props} />
    )
}

Header.Content = SemanticUIHeader.Content
Header.Subheader = SemanticUIHeader.Subheader
