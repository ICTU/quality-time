import React, { useContext } from 'react';
import { Feed as SemanticUIFeed } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Feed(props) {
    return (
        <SemanticUIFeed {...props} />
    )
}

function Date(props) {
    const darkMode = useContext(DarkMode)
    let { style, ...otherProps } = props;
    if (darkMode) {
        if (!style) {
            style = {}
        }
        style.color = "grey"
    }
    return (
        <SemanticUIFeed.Date style={style} {...otherProps} />
    )
}

function Summary(props) {
    const darkMode = useContext(DarkMode)
    let { style, ...otherProps } = props;
    if (darkMode) {
        if (!style) {
            style = {}
        }
        style.color = "white"
    }
    return (
        <SemanticUIFeed.Summary style={style} {...otherProps} />
    )
}

Feed.Content = SemanticUIFeed.Content
Feed.Date = Date
Feed.Event = SemanticUIFeed.Event
Feed.Label = SemanticUIFeed.Label
Feed.Summary = Summary
