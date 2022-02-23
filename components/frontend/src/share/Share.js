import React from 'react';
import { Header } from '../semantic_ui_react_wrappers';
import { PermLinkButton } from '../widgets/Button';

export function Share({ title, url }) {
    return (
        <>
            <Header size="small">
                {title}
            </Header>
            <PermLinkButton url={url} />
        </>
    )
}
