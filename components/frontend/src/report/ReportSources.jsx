import ChecklistIcon from "@mui/icons-material/Checklist"
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted"
import SettingsIcon from "@mui/icons-material/Settings"
import { Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { reportPropType, settingsPropType, sourcePropType } from "../sharedPropTypes"
import { SourceParameter } from "../source/SourceParameter"
import { reloadAfterMassEditSource } from "../source/Sources"
import { SourceTypeRichDescription } from "../source/SourceType"
import { theme } from "../theme"
import { getSourceName, referenceDocumentationURL } from "../utils"
import { UnsortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { TableRowWithDetails } from "../widgets/TableRowWithDetails"
import { Tabs } from "../widgets/Tabs"
import { InfoMessage } from "../widgets/WarningMessage"
import { metricsUsingSource, reportSources, unusedMetricTypesSupportedBySource } from "./report_utils"

function SourceParameters({ reload, report, source, sourceUuid }) {
    const dataModel = useContext(DataModel)
    const sourceType = dataModel.sources[source.type]
    const allParameters = sourceType.parameters
    const defaultLocationParameterKeys = ["url", "landing_url", "username", "password", "private_token"]
    const locationParameterKeys = sourceType?.parameter_layout?.location?.parameters ?? defaultLocationParameterKeys
    let parameters
    if (new Set(Object.keys(allParameters)).intersection(new Set(locationParameterKeys)).size === 0) {
        parameters = <InfoMessage title="No location parameters">This source has no location parameters.</InfoMessage>
    } else {
        parameters = locationParameterKeys.map((key) => (
            <SourceParameter
                fixedEditScope="report"
                key={key}
                report={report}
                source={source}
                sourceUuid={sourceUuid}
                parameter={allParameters[key]}
                parameterKey={key}
                parameterValue={source?.parameters?.[key]}
                reload={(json) => reloadAfterMassEditSource(json, reload)}
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
            />
        ))
    }
    return (
        <Stack spacing={2} margin="10px">
            <SourceTypeRichDescription sourceTypeKey={source.type} />
            {parameters}
        </Stack>
    )
}
SourceParameters.propTypes = {
    reload: func,
    report: reportPropType,
    source: sourcePropType,
    sourceUuid: string,
}

function Metrics({ report, source }) {
    const dataModel = useContext(DataModel)
    const metrics = metricsUsingSource(dataModel, report, source)
    return (
        <TableContainer>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <UnsortableTableHeaderCell label="Subject" />
                        <UnsortableTableHeaderCell label="Metric" />
                    </TableRow>
                </TableHead>
                <TableBody>
                    {Object.entries(metrics).map(([metricUuid, metric]) => (
                        <TableRow
                            key={metricUuid}
                            sx={{
                                "&:nth-of-type(odd)": {
                                    backgroundColor: theme.palette.action.hover,
                                },
                            }}
                        >
                            <TableCell>
                                <a href={"#" + metric.subjectUuid}>{metric.subjectName}</a>
                            </TableCell>
                            <TableCell>
                                <a href={"#" + metricUuid}>
                                    {metric.name}
                                    {metric.secondary_name ? " - " + metric.secondary_name : ""}
                                </a>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
Metrics.propTypes = {
    report: reportPropType,
    source: sourcePropType,
}

function UnusedMetricTypes({ report, source }) {
    const dataModel = useContext(DataModel)
    const unusedMetricTypes = unusedMetricTypesSupportedBySource(dataModel, report, source)
    if (unusedMetricTypes.size === 0) {
        return (
            <InfoMessage title="No unused metric types">
                All metric types that this source supports are being used.
            </InfoMessage>
        )
    }
    return (
        <TableContainer>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <UnsortableTableHeaderCell label="Metric type" />
                        <UnsortableTableHeaderCell label="Description" />
                        <UnsortableTableHeaderCell label="Why measure this metric type?" />
                    </TableRow>
                </TableHead>
                <TableBody>
                    {[...unusedMetricTypes].map((metricType) => (
                        <TableRow
                            key={metricType}
                            sx={{
                                "&:nth-of-type(odd)": {
                                    backgroundColor: theme.palette.action.hover,
                                },
                            }}
                        >
                            <TableCell>
                                <a href={referenceDocumentationURL(dataModel.metrics[metricType].name)}>
                                    {dataModel.metrics[metricType].name}
                                </a>
                            </TableCell>
                            <TableCell>{dataModel.metrics[metricType].description}</TableCell>
                            <TableCell>{dataModel.metrics[metricType].rationale}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
UnusedMetricTypes.propTypes = {
    report: reportPropType,
    source: sourcePropType,
}

function SourceDetails({ reload, report, settings, source, sourceUuid }) {
    const tabs = [
        { label: "Source configuration", icon: <SettingsIcon /> },
        { label: "Metrics using the source", icon: <ChecklistIcon /> },
        { label: "Unused metric types", icon: <FormatListBulletedIcon /> },
    ]
    const panes = [
        <SourceParameters key={sourceUuid} reload={reload} report={report} source={source} sourceUuid={sourceUuid} />,
        <Metrics key="metrics" report={report} source={source} />,
        <UnusedMetricTypes key="unused_metric_types" report={report} source={source} />,
    ]
    return (
        <Tabs settings={settings} tabs={tabs} uuid={sourceUuid}>
            {panes}
        </Tabs>
    )
}
SourceDetails.propTypes = {
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    source: sourcePropType,
    sourceUuid: string,
}

export function ReportSources({ reload, report, settings }) {
    const dataModel = useContext(DataModel)
    const sources = reportSources(dataModel, report)
    if (sources.length === 0) {
        return <InfoMessage title="No sources">No sources have been configured yet.</InfoMessage>
    }
    return (
        <TableContainer>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <UnsortableTableHeaderCell label="Source" />
                        <UnsortableTableHeaderCell label="Source type" />
                        <UnsortableTableHeaderCell label="URL" />
                        <UnsortableTableHeaderCell textAlign="right" label="Number of metrics using the source" />
                        <UnsortableTableHeaderCell
                            textAlign="right"
                            label="Number of metric types not using the source"
                        />
                    </TableRow>
                </TableHead>
                <TableBody>
                    {sources.map((source) => (
                        <TableRowWithDetails
                            details={
                                <SourceDetails
                                    reload={reload}
                                    report={report}
                                    settings={settings}
                                    source={source}
                                    sourceUuid={source.uuid}
                                />
                            }
                            expanded={settings.expandedItems.includes(source.uuid)}
                            key={source.uuid}
                            onExpand={() => settings.expandedItems.toggle(source.uuid)}
                        >
                            <TableCell>{getSourceName(source, dataModel)}</TableCell>
                            <TableCell>{dataModel.sources[source.type].name}</TableCell>
                            <TableCell>{source.parameters?.url ?? ""}</TableCell>
                            <TableCell align="right">{source.nrMetrics}</TableCell>
                            <TableCell align="right">
                                {unusedMetricTypesSupportedBySource(dataModel, report, source).size}
                            </TableCell>
                        </TableRowWithDetails>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
}
ReportSources.propTypes = {
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
