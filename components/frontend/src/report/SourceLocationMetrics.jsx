import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { string } from "prop-types"
import { useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { reportPropType } from "../sharedPropTypes"
import { theme } from "../theme"
import { UnsortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { metricsUsingSourceLocation } from "./report_utils"

export function SourceLocationMetrics({ report, sourceLocationUuid }) {
    const dataModel = useContext(DataModelContext)
    const metrics = metricsUsingSourceLocation(dataModel, report, sourceLocationUuid)
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
SourceLocationMetrics.propTypes = {
    report: reportPropType,
    sourceLocationUuid: string,
}
