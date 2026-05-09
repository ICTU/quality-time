import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { useContext } from "react"

import { DataModelContext } from "../context/DataModel"
import { reportPropType, sourcePropType } from "../sharedPropTypes"
import { theme } from "../theme"
import { UnsortableTableHeaderCell } from "../widgets/TableHeaderCell"
import { metricsUsingSource } from "./report_utils"

export function SourceMetrics({ report, source }) {
    const dataModel = useContext(DataModelContext)
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
SourceMetrics.propTypes = {
    report: reportPropType,
    source: sourcePropType,
}
