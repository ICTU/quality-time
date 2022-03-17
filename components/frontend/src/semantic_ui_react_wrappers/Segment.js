import React, { useContext } from 'react';
import { Segment as SemanticUISegment } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import './Segment.css';

export function Segment(props) {
    return (
        <SemanticUISegment inverted={useContext(DarkMode)} {...props} />
    )
}
