import React from 'react';
import { Icon } from 'semantic-ui-react';
import { Header } from '../semantic_ui_react_wrappers';
import { HyperLink } from '../widgets/HyperLink';
import { slugify } from '../utils';

export function MetricTypeHeader({ metricType }) {
    const url = `https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/reference.html${slugify(metricType.name)}`
    return (
        <Header>
            <Header.Content>
                {metricType.name}
                <Header.Subheader>
                    {metricType.description} <HyperLink url={url}>Read the Docs <Icon name="external" link /></HyperLink>
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}
