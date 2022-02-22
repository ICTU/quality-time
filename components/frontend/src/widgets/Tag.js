import React from 'react';
import { Label } from 'semantic-ui-react';
import "./Tag.css";

export function Tag({ selected, tag }) {
    const color = selected ? "blue" : "gainsboro"
    return (
        <Label color={color} tag>{tag}</Label>
    )
}
