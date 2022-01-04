import React, { useContext } from 'react';
import { Header, Icon, Menu, Tab } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { MetricParameters } from './MetricParameters';
import { PermLinkButton } from '../widgets/Button';
import { FocusableTab } from '../widgets/FocusableTab';
import { ChangeLog } from '../changelog/ChangeLog';

export function MetricConfiguration({ metric, metric_uuid, report, reload }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type]
    const metricUrl = `${window.location}#${metric_uuid}`
    const panes = [
        {
            menuItem: <Menu.Item key='configuration'><Icon name="settings" /><FocusableTab>{'Configuration'}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <MetricParameters metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />
            </Tab.Pane>
        },
        {
            menuItem: <Menu.Item key='changelog'><Icon name="history" /><FocusableTab>{'Changelog'}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <ChangeLog timestamp={report.timestamp} metric_uuid={metric_uuid} />
            </Tab.Pane>
        },
        {
            menuItem: <Menu.Item key="share"><Icon name="share square" /><FocusableTab>{'Share'}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <Header size="small">
                    Metric permanent link
                </Header>
                <PermLinkButton url={metricUrl} />
            </Tab.Pane>
        }
    ];
    return (
        <>
            <Header>
                <Header.Content>
                    {metricType.name}
                    <Header.Subheader>
                        {metricType.description}
                    </Header.Subheader>
                </Header.Content>
            </Header>
            <Tab panes={panes} />
        </>
    )
}
