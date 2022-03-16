import React, { useContext } from 'react';
import { Tab as SemanticUITab } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import './Tab.css';

export function Tab(props) {
    const darkMode = useContext(DarkMode)
    return (
        <SemanticUITab menu={{ inverted: darkMode, attached: !darkMode, tabular: !darkMode }} {...props} />
    )
}

function Pane(props) {
    return (
        <SemanticUITab.Pane inverted={useContext(DarkMode)} {...props} />
    )
}

Tab.Pane = Pane
