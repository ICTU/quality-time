import React from 'react';
import { Breadcrumb } from 'semantic-ui-react';

export function ItemBreadcrumb(props) {
    return (
        <Breadcrumb size={props.size || 'small'}>
            <Breadcrumb.Section>{props.report}</Breadcrumb.Section>
            {props.subject &&
                <>
                    <Breadcrumb.Divider icon='right chevron' />
                    <Breadcrumb.Section>{props.subject}</Breadcrumb.Section>
                    {props.metric &&
                        <>
                            <Breadcrumb.Divider icon='right chevron' />
                            <Breadcrumb.Section>{props.metric}</Breadcrumb.Section>
                        </>
                    }
                </>
            }
        </Breadcrumb>
    )
}
