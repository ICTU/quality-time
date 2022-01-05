import React from 'react';
import { Header } from 'semantic-ui-react';
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
