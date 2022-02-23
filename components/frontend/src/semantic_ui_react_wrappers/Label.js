import React, { useContext } from 'react';
import { Label as SemanticUILabel } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Label(props) {
    return (
        <SemanticUILabel basic={!useContext(DarkMode)} {...props} />
    )
}

Label.Detail = SemanticUILabel.Detail
