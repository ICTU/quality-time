import { bool, func, string } from "prop-types"
import { useContext, useEffect, useState } from "react"
import { Icon, Menu } from "semantic-ui-react"

import { get_metric_measurements } from "../api/measurement"
import { delete_metric, set_metric_attribute } from "../api/metric"
import { activeTabIndex, tabChangeHandler } from "../app_ui_settings"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { Label, Tab } from "../semantic_ui_react_wrappers"
import {
    datePropType,
    metricPropType,
    reportPropType,
    reportsPropType,
    stringsPropType,
    stringsURLSearchQueryPropType,
} from "../sharedPropTypes"
import { SourceEntities } from "../source/SourceEntities"
import { Sources } from "../source/Sources"
import { getMetricScale, getSourceName, isMeasurementRequested } from "../utils"
import { ActionButton, DeleteButton, PermLinkButton, ReorderButtonGroup } from "../widgets/Button"
import { FocusableTab } from "../widgets/FocusableTab"
import { showMessage } from "../widgets/toast"
import { MetricConfigurationParameters } from "./MetricConfigurationParameters"
import { MetricDebtParameters } from "./MetricDebtParameters"
import { MetricTypeHeader } from "./MetricTypeHeader"
import { TrendGraph } from "./TrendGraph"

function RequestMeasurementButton({ metric, metric_uuid, reload }) {
    const measurementRequested = isMeasurementRequested(metric)
    return (
        <ActionButton
            action="Measure"
            disabled={measurementRequested}
            icon="refresh"
            itemType="metric"
            loading={measurementRequested}
            onClick={() => set_metric_attribute(metric_uuid, "measurement_requested", new Date().toISOString(), reload)}
            popup={`Measure this metric as soon as possible`}
        />
    )
}
RequestMeasurementButton.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function Buttons({ isFirstMetric, isLastMetric, metric, metric_uuid, reload, stopFilteringAndSorting, url }) {
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <div style={{ marginTop: "20px" }}>
                    <ReorderButtonGroup
                        first={isFirstMetric}
                        last={isLastMetric}
                        moveable="metric"
                        slot="row"
                        onClick={(direction) => {
                            stopFilteringAndSorting()
                            set_metric_attribute(metric_uuid, "position", direction, reload)
                        }}
                    />
                    <PermLinkButton itemType="metric" url={url} />
                    <RequestMeasurementButton metric={metric} metric_uuid={metric_uuid} reload={reload} />
                    <DeleteButton itemType="metric" onClick={() => delete_metric(metric_uuid, reload)} />
                </div>
            }
        />
    )
}
Buttons.propTypes = {
    isFirstMetric: bool,
    isLastMetric: bool,
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    stopFilteringAndSorting: func,
    url: string,
}

function fetchMeasurements(reportDate, metric_uuid, setMeasurements) {
    get_metric_measurements(metric_uuid, reportDate)
        .then(function (json) {
            if (json.ok !== false) {
                setMeasurements(json.measurements)
            }
            return null
        })
        .catch((error) => showMessage("error", "Could not fetch measurements", `${error}`))
}
fetchMeasurements.propTypes = {
    reportDate: datePropType,
    metric_uuid: string,
    setMeasurements: func,
}

export function MetricDetails({
    changed_fields,
    isFirstMetric,
    isLastMetric,
    metric_uuid,
    reload,
    report_date,
    reports,
    report,
    stopFilteringAndSorting,
    subject_uuid,
    expandedItems,
}) {
    const dataModel = useContext(DataModel)
    const [measurements, setMeasurements] = useState([])
    useEffect(() => {
        fetchMeasurements(report_date, metric_uuid, setMeasurements)
        // eslint-disable-next-line
    }, [metric_uuid, report_date])
    function measurementsReload() {
        reload()
        fetchMeasurements(report_date, metric_uuid, setMeasurements)
    }
    const subject = report.subjects[subject_uuid]
    const metric = subject.metrics[metric_uuid]
    const last_measurement = measurements[measurements.length - 1]
    let any_error = last_measurement?.sources.some((source) => source.connection_error || source.parse_error)
    any_error =
        any_error ||
        Object.values(metric.sources ?? {}).some(
            (source) => !dataModel.metrics[metric.type].sources.includes(source.type),
        )
    const sources_menu_item = any_error ? <Label color="red">{"Sources"}</Label> : "Sources"
    const metricUrl = `${window.location.href.split("#")[0]}#${metric_uuid}`
    let panes = []
    panes.push(
        {
            menuItem: (
                <Menu.Item key="configuration">
                    <Icon name="cogs" />
                    <FocusableTab>{"Configuration"}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <MetricConfigurationParameters
                        subject={subject}
                        metric={metric}
                        metric_uuid={metric_uuid}
                        report={report}
                        reload={reload}
                    />
                </Tab.Pane>
            ),
        },
        {
            menuItem: (
                <Menu.Item key="debt">
                    <Icon name="money" />
                    <FocusableTab>{"Technical debt"}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <MetricDebtParameters metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />
                </Tab.Pane>
            ),
        },
        {
            menuItem: (
                <Menu.Item key="sources">
                    <Icon name="server" />
                    <FocusableTab>{sources_menu_item}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <Sources
                        reports={reports}
                        report={report}
                        metric={metric}
                        metric_uuid={metric_uuid}
                        measurement={metric.latest_measurement}
                        changed_fields={changed_fields}
                        reload={reload}
                    />
                </Tab.Pane>
            ),
        },
        {
            menuItem: (
                <Menu.Item key="changelog">
                    <Icon name="history" />
                    <FocusableTab>{"Changelog"}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <ChangeLog timestamp={report.timestamp} metric_uuid={metric_uuid} />
                </Tab.Pane>
            ),
        },
    )
    if (measurements.length > 0) {
        if (getMetricScale(metric, dataModel) !== "version_number") {
            panes.push({
                menuItem: (
                    <Menu.Item key="trend_graph">
                        <Icon
                            className="linegraph"
                            /* Using name="linegraph" results in "Invalid prop `name` of value `linegraph` supplied to `Icon`."
                               Using name="line graph" does not show the icon. Using className works around this. */
                        />
                        <FocusableTab>{"Trend graph"}</FocusableTab>
                    </Menu.Item>
                ),
                render: () => (
                    <Tab.Pane>
                        <TrendGraph metric={metric} measurements={measurements} />
                    </Tab.Pane>
                ),
            })
        }
        last_measurement.sources.forEach((source) => {
            const report_source = metric.sources[source.source_uuid]
            if (!report_source) {
                return
            } // source was deleted, continue
            const nr_entities = source.entities?.length ?? 0
            if (nr_entities === 0) {
                return
            } // no entities to show, continue
            const source_name = getSourceName(report_source, dataModel)
            panes.push({
                menuItem: (
                    <Menu.Item key={source.source_uuid}>
                        <FocusableTab>{source_name}</FocusableTab>
                    </Menu.Item>
                ),
                render: () => (
                    <Tab.Pane>
                        <SourceEntities
                            report={report}
                            metric={metric}
                            metric_uuid={metric_uuid}
                            source={source}
                            reload={measurementsReload}
                        />
                    </Tab.Pane>
                ),
            })
        })
    }

    return (
        <>
            <MetricTypeHeader metricType={dataModel.metrics[metric.type]} />
            <Tab
                defaultActiveIndex={activeTabIndex(expandedItems, metric_uuid)}
                onTabChange={tabChangeHandler(expandedItems, metric_uuid)}
                panes={panes}
            />
            <Buttons
                metric={metric}
                metric_uuid={metric_uuid}
                isFirstMetric={isFirstMetric}
                isLastMetric={isLastMetric}
                reload={reload}
                stopFilteringAndSorting={stopFilteringAndSorting}
                url={metricUrl}
            />
        </>
    )
}
MetricDetails.propTypes = {
    changed_fields: stringsPropType,
    isFirstMetric: bool,
    isLastMetric: bool,
    metric_uuid: string,
    reload: func,
    report_date: datePropType,
    reports: reportsPropType,
    report: reportPropType,
    stopFilteringAndSorting: func,
    subject_uuid: string,
    expandedItems: stringsURLSearchQueryPropType,
}
