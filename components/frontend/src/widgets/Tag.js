import React from 'react';
import { Label } from 'semantic-ui-react';
import "./Tag.css";

export function Tag(props) {
    return (
        <Label color={props.color} tag>{props.tag}</Label>
    )
}
