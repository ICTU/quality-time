import React, { useContext } from 'react';
import { Feed as SemanticUIFeed } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import { addInvertedClassNameWhenInDarkMode } from './dark_mode';
import './Feed.css';

export function Feed(props) {
    return (
        <SemanticUIFeed {...props} />
    )
}

function Date(props) {
    return (
        <SemanticUIFeed.Date {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
    )
}

function Summary(props) {
    return (
        <SemanticUIFeed.Summary {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
    )
}

Feed.Content = SemanticUIFeed.Content
Feed.Date = Date
Feed.Event = SemanticUIFeed.Event
Feed.Label = SemanticUIFeed.Label
Feed.Summary = Summary
