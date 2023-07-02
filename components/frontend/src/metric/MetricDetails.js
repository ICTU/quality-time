import React, { useContext, useEffect, useState } from 'react';
import { Icon, Menu } from 'semantic-ui-react';
import { Label, Tab } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { Sources } from '../source/Sources';
import { SourceEntities } from '../source/SourceEntities';
import { FocusableTab } from '../widgets/FocusableTab';
import { DeleteButton, ReorderButtonGroup } from '../widgets/Button';
import { delete_metric, set_metric_attribute } from '../api/metric';
import { get_metric_measurements } from '../api/measurement';
import { get_source_name } from '../utils';
import { ChangeLog } from '../changelog/ChangeLog';
import { Share } from '../share/Share';
import { MetricConfigurationParameters } from './MetricConfigurationParameters';
import { MetricDebtParameters } from './MetricDebtParameters';
import { MetricTypeHeader } from './MetricTypeHeader';
import { TrendGraph } from './TrendGraph';

function Buttons({ metric_uuid, first_metric, last_metric, stopSorting, reload }) {
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <div style={{ marginTop: "20px" }}>
                <ReorderButtonGroup
                    first={first_metric} last={last_metric} moveable="metric" slot="row"
                    onClick={(direction) => { stopSorting(); set_metric_attribute(metric_uuid, "position", direction, reload) }} />
                <DeleteButton item_type="metric" onClick={() => delete_metric(metric_uuid, reload)} />
            </div>}
        />
    )
}

function fetch_measurements(report_date, metric_uuid, setMeasurements) {
    get_metric_measurements(metric_uuid, report_date)
        .then(function (json) {
            if (json.ok !== false) {
                setMeasurements(json.measurements);
            }
        })
}

export function MetricDetails({
    report_date,
    reports,
    report,
    subject_uuid,
    metric_uuid,
    first_metric,
    last_metric,
    stopSorting,
    changed_fields,
    visibleDetailsTabs,
    toggleVisibleDetailsTab,
    reload
}) {
    const dataModel = useContext(DataModel)
    const [measurements, setMeasurements] = useState([]);
    useEffect(() => {
        fetch_measurements(report_date, metric_uuid, setMeasurements);
        // eslint-disable-next-line
    }, [metric_uuid, report_date]);
    function measurementsReload() {
        reload();
        fetch_measurements(report_date, metric_uuid, setMeasurements)
    }
    const subject = report.subjects[subject_uuid];
    const metric = subject.metrics[metric_uuid];
    const last_measurement = measurements[measurements.length - 1];
    let any_error = last_measurement?.sources.some((source) => source.connection_error || source.parse_error);
    any_error = any_error || Object.values(metric.sources ?? {}).some((source) => !dataModel.metrics[metric.type].sources.includes(source.type))
    const sources_menu_item = any_error ? <Label color='red'>{"Sources"}</Label> : "Sources";
    let panes = [];
    panes.push(
        {
            menuItem: <Menu.Item key='configuration'><Icon name="cogs" /><FocusableTab>{'Configuration'}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <MetricConfigurationParameters subject={subject} metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />
            </Tab.Pane>
        },
        {
            menuItem: <Menu.Item key='debt'><Icon name="money" /><FocusableTab>{'Technical debt'}</FocusableTab></Menu.Item>,
            render: () => <Tab.Pane>
                <MetricDebtParameters metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />
            </Tab.Pane>
        },
        {
            menuItem: <Menu.Item key='sources'><Icon name="server" /><FocusableTab>{sources_menu_item}</FocusableTab></Menu.Item>,
            render: () => (
                <Tab.Pane>
                    <Sources
                        reports={reports}
                        report={report}
                        metric={metric}
                        metric_uuid={metric_uuid}
                        measurement={metric.latest_measurement}
                        changed_fields={changed_fields}
                        reload={reload} />
                </Tab.Pane>
            )
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
    );
    if (measurements.length > 0) {
        if (metric.scale !== "version_number") {
            panes.push(
                {
                    menuItem: <Menu.Item key='trend_graph'><Icon name="line graph" /><FocusableTab>{'Trend graph'}</FocusableTab></Menu.Item>,
                    render: () => <Tab.Pane><TrendGraph metric={metric} measurements={measurements} /></Tab.Pane>
                }
            )
        }
        last_measurement.sources.forEach((source) => {
            const report_source = metric.sources[source.source_uuid];
            if (!report_source) { return }  // source was deleted, continue
            const nr_entities = (source.entities && source.entities.length) || 0;
            if (nr_entities === 0) { return } // no entities to show, continue
            const source_name = get_source_name(report_source, dataModel);
            panes.push({
                menuItem: <Menu.Item key={source.source_uuid}><FocusableTab>{source_name}</FocusableTab></Menu.Item>,
                render: () => <Tab.Pane><SourceEntities report={report} metric={metric} metric_uuid={metric_uuid} source={source} reload={measurementsReload} /></Tab.Pane>
            });
        });
    }
    const metricUrl = `${window.location}#${metric_uuid}`

    function onTabChange(_event, data) {
        const old_tab = visibleDetailsTabs.filter((tab) => tab?.startsWith(metric_uuid))[0];
        const new_tab = `${metric_uuid}:${data.activeIndex}`;
        toggleVisibleDetailsTab(old_tab, new_tab);
    }

    const visible_tabs = visibleDetailsTabs.filter((tab) => tab?.startsWith(metric_uuid));
    const defaultActiveTab = visible_tabs.length > 0 ? Number(visible_tabs[0].split(":")[1]) : 0;
    const metricType = dataModel.metrics[metric.type];
    return (
        <>
            <MetricTypeHeader metricType={metricType} />
            <Tab panes={panes} defaultActiveIndex={defaultActiveTab} onTabChange={onTabChange} />
            <Buttons metric_uuid={metric_uuid} first_metric={first_metric} last_metric={last_metric} stopSorting={stopSorting} reload={reload} />
        </>
    );
}
