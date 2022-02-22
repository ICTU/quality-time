import React, { useContext } from 'react';
import { DarkMode } from '../context/DarkMode';
import './FocusableTab.css';

export function FocusableTab(props) {
    const className = useContext(DarkMode) ? "tabbutton inverted" : "tabbutton"
    return (
        <button className={className}>
            {props.children}
        </button>
    );
}
