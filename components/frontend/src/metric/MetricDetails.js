import { bool, func, string } from "prop-types"
import { useContext, useEffect, useState } from "react"

import { get_metric_measurements } from "../api/measurement"
import { delete_metric, set_metric_attribute } from "../api/metric"
import { activeTabIndex, tabChangeHandler } from "../app_ui_settings"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { Tab } from "../semantic_ui_react_wrappers"
import {
    datePropType,
    metricPropType,
    reportPropType,
    reportsPropType,
    stringsPropType,
    stringsURLSearchQueryPropType,
} from "../sharedPropTypes"
import { Logo } from "../source/Logo"
import { SourceEntities } from "../source/SourceEntities"
import { Sources } from "../source/Sources"
import { getSourceName, isMeasurementRequested } from "../utils"
import { ActionButton, DeleteButton, PermLinkButton, ReorderButtonGroup } from "../widgets/Button"
import { changelogTabPane, configurationTabPane, tabPane } from "../widgets/TabPane"
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

function fetchMeasurements(reportDate, metric_uuid, setMeasurements, setMeasurementsStatus) {
    get_metric_measurements(metric_uuid, reportDate)
        .then(function (json) {
            setMeasurements(json.measurements ?? [])
            setMeasurementsStatus("loaded")
            return null
        })
        .catch((error) => {
            showMessage("error", "Could not fetch measurements", `${error}`)
            setMeasurementsStatus("failed")
        })
}
fetchMeasurements.propTypes = {
    metric_uuid: string,
    reportDate: datePropType,
    setMeasurements: func,
    setMeasurementsStatus: func,
}

export function MetricDetails({
    changed_fields,
    isFirstMetric,
    isLastMetric,
    metric_uuid,
    reload,
    reportDate,
    reports,
    report,
    stopFilteringAndSorting,
    subject_uuid,
    expandedItems,
}) {
    const dataModel = useContext(DataModel)
    const [measurements, setMeasurements] = useState([])
    const [measurementsStatus, setMeasurementsStatus] = useState("loading")
    useEffect(() => {
        fetchMeasurements(reportDate, metric_uuid, setMeasurements, setMeasurementsStatus)
        // eslint-disable-next-line
    }, [metric_uuid, reportDate])
    function measurementsReload() {
        reload()
        fetchMeasurements(reportDate, metric_uuid, setMeasurements, setMeasurementsStatus)
    }
    const subject = report.subjects[subject_uuid]
    const metric = subject.metrics[metric_uuid]
    const lastMeasurement = measurements[measurements.length - 1]
    let anyError = lastMeasurement?.sources.some((source) => source.connection_error || source.parse_error)
    anyError =
        anyError ||
        Object.values(metric.sources ?? {}).some(
            (source) => !dataModel.metrics[metric.type].sources.includes(source.type),
        )
    const metricUrl = `${window.location.href.split("#")[0]}#${metric_uuid}`
    let panes = []
    panes.push(
        configurationTabPane(
            <MetricConfigurationParameters
                subject={subject}
                metric={metric}
                metric_uuid={metric_uuid}
                report={report}
                reload={reload}
            />,
        ),
        tabPane(
            "Technical debt",
            <MetricDebtParameters metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />,
            { iconName: "money" },
        ),
        tabPane(
            "Sources",
            <Sources
                reports={reports}
                report={report}
                metric={metric}
                metric_uuid={metric_uuid}
                measurement={metric.latest_measurement}
                changed_fields={changed_fields}
                reload={reload}
            />,
            { iconName: "server", error: Boolean(anyError) },
        ),
        changelogTabPane(<ChangeLog timestamp={report.timestamp} metric_uuid={metric_uuid} />),
        tabPane(
            "Trend graph",
            <TrendGraph metric={metric} measurements={measurements} loading={measurementsStatus} />,
            { iconName: "linegraph" },
        ),
    )
    if (measurements.length > 0) {
        lastMeasurement.sources.forEach((source) => {
            const reportSource = metric.sources[source.source_uuid]
            if (!reportSource) {
                return
            } // source was deleted, continue
            const nrEntities = source.entities?.length ?? 0
            if (nrEntities === 0) {
                return
            } // no entities to show, continue
            const sourceName = getSourceName(reportSource, dataModel)
            panes.push(
                tabPane(
                    sourceName,
                    <SourceEntities
                        report={report}
                        metric={metric}
                        metric_uuid={metric_uuid}
                        source={source}
                        reload={measurementsReload}
                    />,
                    { image: <Logo logo={reportSource.type} alt={sourceName} /> },
                ),
            )
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
    reportDate: datePropType,
    reports: reportsPropType,
    report: reportPropType,
    stopFilteringAndSorting: func,
    subject_uuid: string,
    expandedItems: stringsURLSearchQueryPropType,
}
