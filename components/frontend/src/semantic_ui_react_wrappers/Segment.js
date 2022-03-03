import React, { useContext } from 'react';
import { Segment as SemanticUISegment } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Segment(props) {
    return (
        <SemanticUISegment inverted={useContext(DarkMode)} {...props} />
    )
}
