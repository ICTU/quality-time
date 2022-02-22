import React, { useContext } from 'react';
import { Icon as SemanticUIIcon } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Icon(props) {
    return (
        <SemanticUIIcon inverted={useContext(DarkMode)} {...props} />
    )
}
