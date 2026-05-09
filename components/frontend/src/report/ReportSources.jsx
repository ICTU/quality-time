import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { func } from "prop-types"
import { useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { reportPropType, settingsPropType } from "../sharedPropTypes"
import { getSourceName, getSourceTypeName } from "../utils"
import { UnsortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { TableRowWithDetails } from "../widgets/TableRowWithDetails"
import { InfoMessage } from "../widgets/WarningMessage"
import { reportSources, unusedMetricTypesSupportedBySource } from "./report_utils"
import { SourceDetails } from "./SourceDetails"

export function ReportSources({ reload, report, settings }) {
    const dataModel = useContext(DataModelContext)
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
                            firstCellContent={getSourceName(source, dataModel)}
                        >
                            <TableCell>{getSourceTypeName(source, dataModel)}</TableCell>
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
