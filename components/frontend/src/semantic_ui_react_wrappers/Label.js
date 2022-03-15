import React, { useContext } from 'react';
import { Label as SemanticUILabel } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import './Label.css';

export function Label(props) {
    return (
        <SemanticUILabel basic={!useContext(DarkMode)} {...props} />
    )
}

Label.Detail = SemanticUILabel.Detail
