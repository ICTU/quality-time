import { Breadcrumb } from '../semantic_ui_react_wrappers';
import { string } from 'prop-types';

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
                            {props.source &&
                                <>
                                    <Breadcrumb.Divider icon='right chevron' />
                                    <Breadcrumb.Section>{props.source}</Breadcrumb.Section>
                                </>
                            }
                        </>
                    }
                </>
            }
        </Breadcrumb>
    )
}
ItemBreadcrumb.propTypes = {
    metric: string,
    report: string,
    size: string,
    source: string,
    subject: string,
}
