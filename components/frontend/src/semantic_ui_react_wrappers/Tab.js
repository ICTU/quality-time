import React, { useContext } from 'react';
import { Tab as SemanticUITab } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Tab(props) {
    return (
        <SemanticUITab menu={{ inverted: useContext(DarkMode), attached: true, tabular: true }} {...props} />
    )
}

function Pane(props) {
    return (
        <SemanticUITab.Pane inverted={useContext(DarkMode)} {...props} />
    )
}

Tab.Pane = Pane
