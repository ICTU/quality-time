import React, { useContext } from 'react';
import { Card as SemanticUICard } from 'semantic-ui-react';
import { DarkMode } from '../context/DarkMode';
import { addInvertedClassNameWhenInDarkMode } from './dark_mode';
import './Card.css';

export function Card(props) {
    return (
        <SemanticUICard {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
    )
}

function Header(props) {
    return (
        <SemanticUICard.Header {...addInvertedClassNameWhenInDarkMode(props, useContext(DarkMode))} />
    )
}

Card.Content = SemanticUICard.Content
Card.Header = Header
