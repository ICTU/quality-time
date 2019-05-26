import React from 'react';
import './FocusableTab.css';

export function FocusableTab(props) {
    return (
        <button className="tabbutton">
            {props.children}
        </button>
    );
}
