import React, { useContext } from 'react';
import { Segment as SemanticUISegment } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Segment(props) {
    const darkMode = useContext(DarkMode)
    let {style, ...otherProps} = props;
    if (!darkMode) {
        if (!style) {
            style = {}
        }
        style.backgroundColor = "white"
    }
    return (
        <SemanticUISegment inverted={darkMode} style={style} {...otherProps} />
    )
}
