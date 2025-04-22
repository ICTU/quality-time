import { Stack, Table, TableBody, TableCell, TableContainer, TableFooter, TableHead, TableRow } from "@mui/material"
import { func, string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION } from "../context/Permissions"
import { zIndexTableHeader } from "../defaults"
import { reportPropType, settingsPropType, sourcePropType } from "../sharedPropTypes"
import { SourceParameter } from "../source/SourceParameter"
import { reloadAfterMassEditSource } from "../source/Sources"
import { SourceTypeRichDescription } from "../source/SourceType"
import { UnsortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { TableRowWithDetails } from "../widgets/TableRowWithDetails"
import { InfoMessage } from "../widgets/WarningMessage"
import { reportSources } from "./report_utils"

export function SourceParameters({ reload, report, source, sourceUuid }) {
    const dataModel = useContext(DataModel)
    const allParameters = dataModel.sources[source.type].parameters
    const locationParameterKeys = ["url", "landing_url", "username", "password", "private_token"]
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
                parameterValue={source?.[key]}
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

export function ReportSources({ reload, report, settings }) {
    const dataModel = useContext(DataModel)
    const sources = reportSources(report)
    if (sources.length === 0) {
        return <InfoMessage title="No sources">No sources have been configured yet.</InfoMessage>
    }
    return (
        <TableContainer sx={{ overflowX: "visible" }}>
            <Table
                stickyHeader
                sx={{
                    "& .MuiTableCell-sizeMedium": {
                        padding: "8px 8px",
                    },
                }}
            >
                <TableHead sx={{ bgcolor: "background.default", zIndex: zIndexTableHeader }}>
                    <TableRow>
                        <UnsortableTableHeaderCell colSpan="2" label="Source" />
                        <UnsortableTableHeaderCell label="Source type" />
                        <UnsortableTableHeaderCell label="URL" />
                        <UnsortableTableHeaderCell textAlign="right" label="Number of metrics using the source" />
                    </TableRow>
                </TableHead>
                <TableBody>
                    {sources.map((source) => (
                        <TableRowWithDetails
                            details={
                                <SourceParameters
                                    reload={reload}
                                    report={report}
                                    source={source}
                                    sourceUuid={source.uuid}
                                />
                            }
                            expanded={settings.expandedItems.includes(source.uuid)}
                            key={source.uuid}
                            onExpand={() => settings.expandedItems.toggle(source.uuid)}
                        >
                            <TableCell>{source.name || dataModel.sources[source.type].name}</TableCell>
                            <TableCell>{dataModel.sources[source.type].name}</TableCell>
                            <TableCell>{source.url}</TableCell>
                            <TableCell align="right">{source.nrMetrics}</TableCell>
                        </TableRowWithDetails>
                    ))}
                </TableBody>
                <TableFooter />
            </Table>
        </TableContainer>
    )
}
ReportSources.propTypes = {
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
