import MoneyIcon from "@mui/icons-material/Money"
import ShowChartIcon from "@mui/icons-material/ShowChart"
import StorageIcon from "@mui/icons-material/Storage"
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
import { ButtonRow } from "../widgets/ButtonRow"
import { ActionButton } from "../widgets/buttons/ActionButton"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { PermLinkButton } from "../widgets/buttons/PermLinkButton"
import { ReorderButtonGroup } from "../widgets/buttons/ReorderButtonGroup"
import { RefreshIcon } from "../widgets/icons"
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
            icon={<RefreshIcon />}
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

function MetricDetailsButtonRow({
    isFirstMetric,
    isLastMetric,
    metric,
    metric_uuid,
    reload,
    stopFilteringAndSorting,
    url,
}) {
    const deleteButton = <DeleteButton itemType="metric" onClick={() => delete_metric(metric_uuid, reload)} />
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow rightButton={deleteButton}>
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
                </ButtonRow>
            }
        />
    )
}
MetricDetailsButtonRow.propTypes = {
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
            showMessage("error", "Could not fetch measurements", `${error.message}`)
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
    }, [metric_uuid, reportDate])
    function measurementsReload() {
        reload()
        fetchMeasurements(reportDate, metric_uuid, setMeasurements, setMeasurementsStatus)
    }
    const subject = report.subjects[subject_uuid]
    const metric = subject.metrics[metric_uuid]
    const lastMeasurement = measurements[measurements.length - 1]
    let anyError = lastMeasurement?.sources.some((source) => source.connection_error || source.parse_error)
    let anyWarning = Object.values(metric.sources).some((source) => dataModel.sources[source.type].deprecated)
    anyError =
        anyError ||
        Object.values(metric.sources).some((source) => !dataModel.metrics[metric.type].sources.includes(source.type))
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
            { icon: <StorageIcon />, error: Boolean(anyError), warning: Boolean(anyWarning) },
        ),
        tabPane(
            "Technical debt",
            <MetricDebtParameters metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />,
            { icon: <MoneyIcon /> },
        ),
        changelogTabPane(<ChangeLog timestamp={report.timestamp} metric_uuid={metric_uuid} />),
        tabPane(
            "Trend graph",
            <TrendGraph metric={metric} measurements={measurements} loading={measurementsStatus} />,
            { icon: <ShowChartIcon /> },
        ),
    )
    Object.entries(metric.sources).forEach(([source_uuid, source]) => {
        const sourceName = getSourceName(source, dataModel)
        panes.push(
            tabPane(
                sourceName,
                <SourceEntities
                    loading={measurementsStatus}
                    measurements={measurements}
                    metric={metric}
                    metric_uuid={metric_uuid}
                    reload={measurementsReload}
                    report={report}
                    source_uuid={source_uuid}
                />,
                { image: <Logo logo={source.type} alt={sourceName} /> },
            ),
        )
    })

    return (
        <>
            <MetricTypeHeader metricType={dataModel.metrics[metric.type]} />
            <Tab
                defaultActiveIndex={activeTabIndex(expandedItems, metric_uuid)}
                onTabChange={tabChangeHandler(expandedItems, metric_uuid)}
                panes={panes}
            />
            <MetricDetailsButtonRow
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
