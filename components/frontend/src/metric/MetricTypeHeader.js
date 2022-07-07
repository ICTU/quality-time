import React from 'react';
import { Icon } from 'semantic-ui-react';
import { Header, Popup } from '../semantic_ui_react_wrappers';

function seeAlso(key, urls) {
    return (
        <div key={key}>
            <Header>See also</Header>
            <ol>
                {urls.map((url) => <li key={url}><a href={url}>{url}</a></li>)}
            </ol>
        </div>
    )
}

export function MetricTypeHeader({ metricType }) {
    let popup = null;
    const popupContents = [];
    if (metricType.rationale) {
        popupContents.push(<Header key="rationale-header">Why measure {metricType.name.toLowerCase()}?</Header>)
        popupContents.push(<p key="rationale-text">{metricType.rationale}</p>)
        if (metricType.rationale_urls?.length > 0) {
            popupContents.push(seeAlso("rationale-urls", metricType.rationale_urls))
        }
    }
    if (metricType.explanation) {
        popupContents.push(<Header key="explanation=header">More information</Header>)
        popupContents.push(<p key="explanation-text">{metricType.explanation}</p>)
        if (metricType.explanation_urls?.length > 0) {
            popupContents.push(seeAlso("explanation-urls", metricType.explanation_urls))
        }
    }
    if (popupContents.length > 0) {
        popup = <Popup
            content={<>{popupContents}</>}
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
                    {metricType.description}{popup}
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}
