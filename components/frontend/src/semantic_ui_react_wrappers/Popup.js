import React, { useContext } from 'react';
import { Popup as SemanticUIPopup } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Popup(props) {
    return (
        <SemanticUIPopup inverted={useContext(DarkMode)} {...props} />
    )
}

Popup.Content = SemanticUIPopup.Content
