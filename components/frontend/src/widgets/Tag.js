import React from 'react';
import { Label } from 'semantic-ui-react';

export function Tag(props) {
    return (
        <Label tag>{props.tag}</Label>
    )
}
