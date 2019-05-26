import React from 'react';
import { Label } from 'semantic-ui-react';

function Tag(props) {
    return (
        <Label tag>{props.tag}</Label>
    )
}

export { Tag };