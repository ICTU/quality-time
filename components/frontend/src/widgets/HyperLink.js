import { useContext } from 'react';
import { bool, string } from 'prop-types';
import { DarkMode } from '../context/DarkMode';
import './HyperLink.css';
import { childrenPropType } from '../sharedPropTypes';

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
HyperLink.propTypes = {
    url: string,
    children: childrenPropType,
    error: bool,
}
