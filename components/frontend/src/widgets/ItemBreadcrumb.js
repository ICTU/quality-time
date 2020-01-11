import React from 'react';
import { Breadcrumb } from 'semantic-ui-react';

export function ItemBreadcrumb(props) {
    return (
        <Breadcrumb>
            <Breadcrumb.Section>{props.report}</Breadcrumb.Section>
            <Breadcrumb.Divider icon='right chevron' />
            <Breadcrumb.Section>{props.subject}</Breadcrumb.Section>
            {props.metric &&
                <>
                    <Breadcrumb.Divider icon='right chevron' />
                    <Breadcrumb.Section>{props.metric}</Breadcrumb.Section>
                </>
            }
        </Breadcrumb>
    )
}