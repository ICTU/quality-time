import React, { useContext } from 'react';
import { Label as SemanticUILabel } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import { addInvertedClassNameWhenInDarkMode } from './dark_mode';
import './Label.css';

export function Label(props) {
    return (
        <SemanticUILabel {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
    )
}

Label.Detail = SemanticUILabel.Detail
