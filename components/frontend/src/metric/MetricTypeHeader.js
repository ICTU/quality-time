import React from 'react';
import { Icon } from 'semantic-ui-react';
import { Header, Popup } from '../semantic_ui_react_wrappers';

export function MetricTypeHeader({ metricType }) {
    const rationale = metricType.rationale ? <Popup
        on={['hover', 'focus']}
        wide="very"
        trigger={
            <span>&nbsp;<Icon role="tooltip" aria-label="help" tabIndex="0" name="info circle" /></span>
        }
        content={<><Header>Why measure {metricType.name.toLowerCase()}?</Header>{metricType.rationale}</>}
    /> : null;
    return (
        <Header>
            <Header.Content>
                {metricType.name}
                <Header.Subheader>
                    {metricType.description}{rationale}
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}
