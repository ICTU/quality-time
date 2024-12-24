import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tooltip,
    Typography,
} from "@mui/material"
import { string } from "prop-types"
import { useContext } from "react"

import { DataModel } from "../context/DataModel"
import { datesPropType, measurementsPropType, metricPropType, reportPropType } from "../sharedPropTypes"
import { getMetricResponseOverrun, pluralize } from "../utils"
import { StatusIcon } from "./StatusIcon"

function formatDays(days) {
    return `${days} ${pluralize("day", days)}`
}

export function Overrun({ metric_uuid, metric, report, measurements, dates }) {
    const dataModel = useContext(DataModel)
    const { totalOverrun, overruns } = getMetricResponseOverrun(metric_uuid, metric, report, measurements, dataModel)
    if (totalOverrun === 0) {
        return null
    }
    const triggerText = formatDays(totalOverrun)
    let trigger = <span>{triggerText}</span>
    const sortedDates = dates.slice().sort((d1, d2) => d1.getTime() > d2.getTime())
    const period = `${sortedDates.at(0).toLocaleDateString()} - ${sortedDates.at(-1).toLocaleDateString()}`
    const content = (
        <>
            <Typography>Metric reaction time overruns in the period {period}</Typography>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell textAlign="center" colSpan="3">
                                When did the metric need action?
                            </TableCell>
                            <TableCell textAlign="center" colSpan="3">
                                How long did it take to react?
                            </TableCell>
                        </TableRow>
                        <TableRow>
                            <TableCell textAlign="center">Status</TableCell>
                            <TableCell textAlign="center">Start</TableCell>
                            <TableCell textAlign="center">End</TableCell>
                            <TableCell textAlign="right">Actual</TableCell>
                            <TableCell textAlign="right">Desired</TableCell>
                            <TableCell textAlign="right">Overrun</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {overruns.map((overrun) => (
                            <TableRow key={overrun.start}>
                                <TableCell textAlign="center">
                                    <StatusIcon size="small" status={overrun.status} />
                                </TableCell>
                                <TableCell>{overrun.start.split("T")[0]}</TableCell>
                                <TableCell>{overrun.end.split("T")[0]}</TableCell>
                                <TableCell textAlign="right">{formatDays(overrun.actual_response_time)}</TableCell>
                                <TableCell textAlign="right">{formatDays(overrun.desired_response_time)}</TableCell>
                                <TableCell textAlign="right">{formatDays(overrun.overrun)}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                    <TableHead>
                        <TableRow>
                            <TableCell colSpan="5">
                                <b>Total</b>
                            </TableCell>
                            <TableCell textAlign="right">
                                <b>{triggerText}</b>
                            </TableCell>
                        </TableRow>
                    </TableHead>
                </Table>
            </TableContainer>
        </>
    )
    return (
        <Tooltip slotProps={{ tooltip: { sx: { maxWidth: "32em" } } }} title={content}>
            {trigger}
        </Tooltip>
    )
}
Overrun.propTypes = {
    dates: datesPropType,
    measurements: measurementsPropType,
    metric: metricPropType,
    metric_uuid: string,
    report: reportPropType,
}
