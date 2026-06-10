import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { string } from "prop-types"
import { useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { reportPropType } from "../sharedPropTypes"
import { theme } from "../theme"
import { referenceDocumentationURL } from "../utils"
import { UnsortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { InfoMessage } from "../widgets/WarningMessage"
import { unusedMetricTypesSupportedBySourceLocation } from "./report_utils"

export function UnusedMetricTypes({ report, sourceLocationUuid }) {
    const dataModel = useContext(DataModelContext)
    const unusedMetricTypes = unusedMetricTypesSupportedBySourceLocation(dataModel, report, sourceLocationUuid)
    if (unusedMetricTypes.size === 0) {
        return (
            <InfoMessage title="No unused metric types">
                All metric types that this source location supports are being used.
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
    sourceLocationUuid: string,
}
