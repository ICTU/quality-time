import React, { useContext } from 'react';
import { Label } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import "./Tag.css";

export function Tag({ selected, tag }) {
    const defaultColor = useContext(DarkMode) ? "grey" : null
    const color = selected ? "blue" : defaultColor
    return (
        <Label color={color} tag>{tag}</Label>
    )
}
