import HistoryIcon from "@mui/icons-material/History"
import MoneyIcon from "@mui/icons-material/Money"
import SettingsIcon from "@mui/icons-material/Settings"
import ShowChartIcon from "@mui/icons-material/ShowChart"
import StorageIcon from "@mui/icons-material/Storage"
import { Stack } from "@mui/material"
import { bool, func, string } from "prop-types"
import { useContext, useEffect, useRef, useState } from "react"

import { getMetricMeasurements } from "../api/measurement"
import { deleteMetric, setMetricAttribute } from "../api/metric"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { SnackbarContext } from "../context/Snackbar"
import {
    datePropType,
    metricPropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { Logo } from "../source/Logo"
import { SourceEntities } from "../source/SourceEntities"
import { Sources } from "../source/Sources"
import { getSourceName, isMeasurementRequested, isSourceConfigurationComplete } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { ActionButton } from "../widgets/buttons/ActionButton"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { PermLinkButton } from "../widgets/buttons/PermLinkButton"
import { ReorderButtonGroup } from "../widgets/buttons/ReorderButtonGroup"
import { RefreshIcon } from "../widgets/icons"
import { Tabs } from "../widgets/Tabs"
import { MetricConfigurationParameters } from "./MetricConfigurationParameters"
import { MetricDebtParameters } from "./MetricDebtParameters"
import { TrendGraph } from "./TrendGraph"

export const METRIC_NAME_TAB_INDEX = 0
export const METRIC_DEBT_TAB_INDEX = 2
export const TREND_GRAPH_TAB_INDEX = 4

function RequestMeasurementButton({ metric, metricUuid, reload }) {
    const dataModel = useContext(DataModelContext)
    const configurationComplete = isSourceConfigurationComplete(dataModel, metric)
    const measurementRequested = isMeasurementRequested(metric)
    return (
        <ActionButton
            action="Measure"
            disabled={!configurationComplete || measurementRequested}
            icon={<RefreshIcon />}
            itemType="metric"
            loading={measurementRequested}
            onClick={() => setMetricAttribute(metricUuid, "measurement_requested", new Date().toISOString(), reload)}
            popup={
                configurationComplete
                    ? "Measure this metric as soon as possible"
                    : "The source configuration of this metric is not complete. Add at least one source and make sure all mandatory parameters for all sources have been provided."
            }
        />
    )
}
RequestMeasurementButton.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
}

function MetricDetailsButtonRow({
    isFirstMetric,
    isLastMetric,
    metric,
    metricUuid,
    reload,
    settings,
    stopFilteringAndSorting,
    url,
}) {
    const deleteButton = (
        <DeleteButton
            itemType="metric"
            onClick={() => {
                deleteMetric(metricUuid, reload)
                settings.expandedItems.deleteItem(metricUuid)
            }}
        />
    )
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow paddingBottom={1} paddingLeft={0} paddingRight={0} paddingTop={2} rightButton={deleteButton}>
                    <ReorderButtonGroup
                        first={isFirstMetric}
                        last={isLastMetric}
                        moveable="metric"
                        slot="row"
                        onClick={(direction) => {
                            stopFilteringAndSorting()
                            setMetricAttribute(metricUuid, "position", direction, reload)
                        }}
                    />
                    <PermLinkButton itemType="metric" url={url} />
                    <RequestMeasurementButton metric={metric} metricUuid={metricUuid} reload={reload} />
                </ButtonRow>
            }
        />
    )
}
MetricDetailsButtonRow.propTypes = {
    isFirstMetric: bool,
    isLastMetric: bool,
    metric: metricPropType,
    metricUuid: string,
    reload: func,
    settings: settingsPropType,
    stopFilteringAndSorting: func,
    url: string,
}

function fetchMeasurements(reportDate, metricUuid, setMeasurements, setMeasurementsStatus, showMessage) {
    getMetricMeasurements(metricUuid, reportDate)
        .then(function (json) {
            if (json.ok === false) {
                showMessage({
                    severity: "error",
                    title: "Could not fetch measurements",
                    description: `${json.statusText}`,
                })
                setMeasurementsStatus("failed")
            } else {
                setMeasurements(json.measurements ?? [])
                setMeasurementsStatus("loaded")
            }
            return null
        })
        .catch((error) => {
            showMessage({ severity: "error", title: "Could not fetch measurements", description: `${error.message}` })
            setMeasurementsStatus("failed")
        })
}
fetchMeasurements.propTypes = {
    metricUuid: string,
    reportDate: datePropType,
    setMeasurements: func,
    setMeasurementsStatus: func,
    showMessage: func,
}

export function MetricDetails({
    changedFields,
    isFirstMetric,
    isLastMetric,
    metricUuid,
    reload,
    reportDate,
    reports,
    report,
    settings,
    stopFilteringAndSorting,
    subjectUuid,
}) {
    const dataModel = useContext(DataModelContext)
    const showMessageRef = useRef(useContext(SnackbarContext))
    const [measurements, setMeasurements] = useState([])
    const [measurementsStatus, setMeasurementsStatus] = useState("loading")
    useEffect(() => {
        fetchMeasurements(reportDate, metricUuid, setMeasurements, setMeasurementsStatus, showMessageRef.current)
    }, [metricUuid, reportDate])
    function measurementsReload() {
        reload()
        fetchMeasurements(reportDate, metricUuid, setMeasurements, setMeasurementsStatus, showMessageRef.current)
    }
    const subject = report.subjects[subjectUuid]
    const metric = subject.metrics[metricUuid]
    const lastMeasurement = measurements.at(-1)
    let anyError = lastMeasurement?.sources.some((source) => source.connection_error || source.parse_error)
    let anyWarning = Object.values(metric.sources).some((source) => dataModel.sources[source.type].deprecated)
    anyError =
        anyError ||
        Object.values(metric.sources).some((source) => !dataModel.metrics[metric.type].sources.includes(source.type))
    const anyInfo = lastMeasurement?.sources.some((source) => source.info_message)
    const metricUrl = `${globalThis.location.href.split("#")[0]}#${metricUuid}`
    const panes = [
        <MetricConfigurationParameters
            key="1"
            metric={metric}
            metricUuid={metricUuid}
            reload={reload}
            report={report}
            subject={subject}
        />,
        <Sources
            changedFields={changedFields}
            key="2"
            measurement={metric.latest_measurement}
            metric={metric}
            metricUuid={metricUuid}
            reload={reload}
            report={report}
            reports={reports}
            settings={settings}
        />,
        <MetricDebtParameters key="3" metric={metric} metricUuid={metricUuid} report={report} reload={reload} />,
        <ChangeLog key="4" timestamp={report.timestamp} metricUuid={metricUuid} />,
        <TrendGraph key="5" metric={metric} measurements={measurements} loading={measurementsStatus} />,
    ]
    const tabs = [
        { label: "Configuration", icon: <SettingsIcon /> },
        {
            info: Boolean(anyInfo),
            error: Boolean(anyError),
            label: "Sources",
            icon: <StorageIcon />,
            warning: Boolean(anyWarning),
        },
        { label: "Technical debt", icon: <MoneyIcon /> },
        { label: "Changelog", icon: <HistoryIcon /> },
        { label: "Trend graph", icon: <ShowChartIcon /> },
    ]
    for (const [sourceUuid, source] of Object.entries(metric.sources)) {
        const sourceName = getSourceName(source, dataModel)
        tabs.push({
            image: <Logo logo={source.type} alt={sourceName} width="21px" height="21px" marginBottom="6px" />,
            label: sourceName,
        })
        panes.push(
            <SourceEntities
                key={metricUuid}
                loading={measurementsStatus}
                measurements={measurements}
                metric={metric}
                metricUuid={metricUuid}
                reload={measurementsReload}
                report={report}
                settings={settings}
                sourceUuid={sourceUuid}
            />,
        )
    }
    return (
        <Stack>
            <Tabs settings={settings} tabs={tabs} uuid={metricUuid}>
                {panes}
            </Tabs>
            <MetricDetailsButtonRow
                metric={metric}
                metricUuid={metricUuid}
                isFirstMetric={isFirstMetric}
                isLastMetric={isLastMetric}
                reload={reload}
                settings={settings}
                stopFilteringAndSorting={stopFilteringAndSorting}
                url={metricUrl}
            />
        </Stack>
    )
}
MetricDetails.propTypes = {
    changedFields: stringsPropType,
    isFirstMetric: bool,
    isLastMetric: bool,
    metricUuid: string,
    reload: func,
    reportDate: datePropType,
    reports: reportsPropType,
    report: reportPropType,
    settings: settingsPropType,
    stopFilteringAndSorting: func,
    subjectUuid: string,
}
