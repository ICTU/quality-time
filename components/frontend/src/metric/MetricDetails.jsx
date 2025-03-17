import HistoryIcon from "@mui/icons-material/History"
import MoneyIcon from "@mui/icons-material/Money"
import SettingsIcon from "@mui/icons-material/Settings"
import ShowChartIcon from "@mui/icons-material/ShowChart"
import StorageIcon from "@mui/icons-material/Storage"
import { Stack } from "@mui/material"
import { bool, func, string } from "prop-types"
import { useContext, useEffect, useState } from "react"

import { get_metric_measurements } from "../api/measurement"
import { delete_metric, set_metric_attribute } from "../api/metric"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
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
import { showMessage } from "../widgets/toast"
import { MetricConfigurationParameters } from "./MetricConfigurationParameters"
import { MetricDebtParameters } from "./MetricDebtParameters"
import { TrendGraph } from "./TrendGraph"

function RequestMeasurementButton({ metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const configurationComplete = isSourceConfigurationComplete(dataModel, metric)
    const measurementRequested = isMeasurementRequested(metric)
    return (
        <ActionButton
            action="Measure"
            disabled={!configurationComplete || measurementRequested}
            icon={<RefreshIcon />}
            itemType="metric"
            loading={measurementRequested}
            onClick={() => set_metric_attribute(metric_uuid, "measurement_requested", new Date().toISOString(), reload)}
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
    metric_uuid: string,
    reload: func,
}

function MetricDetailsButtonRow({
    isFirstMetric,
    isLastMetric,
    metric,
    metric_uuid,
    reload,
    settings,
    stopFilteringAndSorting,
    url,
}) {
    const deleteButton = (
        <DeleteButton
            itemType="metric"
            onClick={() => {
                delete_metric(metric_uuid, reload)
                settings.expandedItems.deleteItem(metric_uuid)
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
    settings: settingsPropType,
    stopFilteringAndSorting: func,
    url: string,
}

function fetchMeasurements(reportDate, metric_uuid, setMeasurements, setMeasurementsStatus) {
    get_metric_measurements(metric_uuid, reportDate)
        .then(function (json) {
            if (json.ok) {
                setMeasurements(json.measurements ?? [])
                setMeasurementsStatus("loaded")
            } else {
                showMessage("error", "Could not fetch measurements", `${json.statusText}`)
                setMeasurementsStatus("failed")
            }
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
    settings,
    stopFilteringAndSorting,
    subject_uuid,
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
    const panes = [
        <MetricConfigurationParameters
            key="1"
            metric={metric}
            metric_uuid={metric_uuid}
            reload={reload}
            report={report}
            subject={subject}
        />,
        <Sources
            changed_fields={changed_fields}
            key="2"
            measurement={metric.latest_measurement}
            metric={metric}
            metric_uuid={metric_uuid}
            reload={reload}
            report={report}
            reports={reports}
            settings={settings}
        />,
        <MetricDebtParameters key="3" metric={metric} metric_uuid={metric_uuid} report={report} reload={reload} />,
        <ChangeLog key="4" timestamp={report.timestamp} metric_uuid={metric_uuid} />,
        <TrendGraph key="5" metric={metric} measurements={measurements} loading={measurementsStatus} />,
    ]
    const tabs = [
        { label: "Configuration", icon: <SettingsIcon /> },
        { error: Boolean(anyError), label: "Sources", icon: <StorageIcon />, warning: Boolean(anyWarning) },
        { label: "Technical debt", icon: <MoneyIcon /> },
        { label: "Changelog", icon: <HistoryIcon /> },
        { label: "Trend graph", icon: <ShowChartIcon /> },
    ]
    Object.entries(metric.sources).forEach(([source_uuid, source]) => {
        const sourceName = getSourceName(source, dataModel)
        tabs.push({
            image: <Logo logo={source.type} alt={sourceName} width="21px" height="21px" marginBottom="6px" />,
            label: sourceName,
        })
        panes.push(
            <SourceEntities
                key={metric_uuid}
                loading={measurementsStatus}
                measurements={measurements}
                metric={metric}
                metric_uuid={metric_uuid}
                reload={measurementsReload}
                report={report}
                source_uuid={source_uuid}
            />,
        )
    })
    return (
        <Stack>
            <Tabs settings={settings} tabs={tabs} uuid={metric_uuid}>
                {panes}
            </Tabs>
            <MetricDetailsButtonRow
                metric={metric}
                metric_uuid={metric_uuid}
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
    changed_fields: stringsPropType,
    isFirstMetric: bool,
    isLastMetric: bool,
    metric_uuid: string,
    reload: func,
    reportDate: datePropType,
    reports: reportsPropType,
    report: reportPropType,
    settings: settingsPropType,
    stopFilteringAndSorting: func,
    subject_uuid: string,
}
