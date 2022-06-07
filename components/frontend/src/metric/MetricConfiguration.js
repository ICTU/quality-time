import React, { useContext } from 'react';
import { Icon, Menu } from 'semantic-ui-react';
import { Tab } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { MetricParameters } from './MetricParameters';
import { FocusableTab } from '../widgets/FocusableTab';
import { ChangeLog } from '../changelog/ChangeLog';
import { Share } from '../share/Share';
import { MetricTypeHeader } from './MetricTypeHeader';

export function MetricConfiguration({ metric, metric_uuid, subject, report, reload }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type]
    const metricUrl = `${window.location}#${metric_uuid}`
    const panes = [
        {
            menuItem: <Menu.Item key='configuration'><Icon name="settings" /><FocusableTab>{'Configuration'}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <MetricParameters subject={subject} metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />
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
            render: () => <Tab.Pane><Share title="Metric permanent link" url={metricUrl} /></Tab.Pane>
        }
    ];
    return (
        <>
            <MetricTypeHeader metricType={metricType} />
            <Tab panes={panes} />
        </>
    )
}
