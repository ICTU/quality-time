import React, { useContext } from 'react';
import { Button as SemanticUIButton } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Button(props) {
    return (
        <SemanticUIButton inverted={useContext(DarkMode)} {...props} />
    )
}

Button.Group = SemanticUIButton.Group
