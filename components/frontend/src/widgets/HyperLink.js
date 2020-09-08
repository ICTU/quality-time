import React from 'react';

export function HyperLink({ url, children }) {
    return (<a href={url} target="_blank" title="Opens new window or tab" rel="noopener noreferrer">{children}</a>)
}