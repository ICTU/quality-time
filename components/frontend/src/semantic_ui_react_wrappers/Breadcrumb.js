import React, { useContext } from 'react';
import { Breadcrumb as SemanticUIBreadcrumb } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import './Breadcrumb.css';

export function Breadcrumb(props) {
    return (
        <SemanticUIBreadcrumb {...props} />
    )
}

function Divider(props) {
    return (
        <SemanticUIBreadcrumb.Divider inverted={useContext(DarkMode)} {...props} />
    )
}

Breadcrumb.Divider = Divider
Breadcrumb.Section = SemanticUIBreadcrumb.Section
