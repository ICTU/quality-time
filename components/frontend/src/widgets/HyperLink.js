import React, { useContext } from 'react';
import { DarkMode } from '../context/DarkMode';
import './HyperLink.css';

export function HyperLink({ url, children, error }) {
    let className = useContext(DarkMode) ? "inverted" : ""
    if (error) {
        className += " error"
    }
    return (
        <a
            className={className}
            href={url}
            onClick={(event) => event.stopPropagation()}
            rel="noopener noreferrer"
            target="_blank"
            title="Opens new window or tab"
        >
            {children}
        </a>
    )
}
