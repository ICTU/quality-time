import React, { useContext } from 'react';
import { Card as SemanticUICard } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';

export function Card(props) {
    const darkMode = useContext(DarkMode)
    let { style, ...otherProps} = props
    if (darkMode) {
        if (!style) {
            style = {}
        }
        style.backgroundColor = "black"
    }
    return (
        <SemanticUICard style={style} {...otherProps} />
    )
}

function Header(props) {
    const darkMode = useContext(DarkMode)
    let { style, ...otherProps} = props
    if (darkMode) {
        if (!style) {
            style = {}
        }
        style.color = "white"
    }
    return (
        <SemanticUICard.Header style={style} {...otherProps} />
    )
}

Card.Content = SemanticUICard.Content
Card.Header = Header
