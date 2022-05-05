import React from 'react';
import { Icon } from 'semantic-ui-react';
import { Header, Popup } from '../semantic_ui_react_wrappers';

export function MetricTypeHeader({ metricType }) {
    let rationale = null;
    if (metricType.rationale) {
        let rationaleUrls = null;
        if (metricType.rationale_urls) {
            rationaleUrls = <>
                <Header>See also</Header>
                <ul>
                    {metricType.rationale_urls.map((url) => <li key={url}><a href={url}>{url}</a></li>)}
                </ul>
            </>
        }
        rationale = <Popup
            content={
                <>
                    <Header>Why measure {metricType.name.toLowerCase()}?</Header>
                    {metricType.rationale}
                    {rationaleUrls}
                </>
            }
            hoverable
            on={['hover', 'focus']}
            trigger={
                <span>&nbsp;<Icon role="tooltip" aria-label="help" tabIndex="0" name="info circle" /></span>
            }
            wide="very"
        />
    }
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
