import { Typography } from "@mui/material"
import Grid from "@mui/material/Grid"
import { func, oneOfType } from "prop-types"
import { useContext } from "react"

import { setReportAttribute } from "../api/report"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { STATUS_DESCRIPTION, STATUS_NAME, statusPropType } from "../metric/status"
import { entityStatusPropType, reportPropType } from "../sharedPropTypes"
import { SOURCE_ENTITY_STATUS_DESCRIPTION, SOURCE_ENTITY_STATUS_NAME } from "../source/source_entity_status"
import { getDesiredResponseTime } from "../utils"

function DesiredResponseTimeInput({ reload, report, status }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const desiredResponseTimes = report.desired_response_times ?? {}
    const inputId = `desired-response-time-${status}`
    const label = STATUS_NAME[status] || SOURCE_ENTITY_STATUS_NAME[status]
    const help = STATUS_DESCRIPTION[status] || SOURCE_ENTITY_STATUS_DESCRIPTION[status]
    return (
        <TextField
            disabled={disabled}
            endAdornment="days"
            helperText={help}
            id={inputId}
            label={label}
            onChange={(value) => {
                desiredResponseTimes[status] = Number.parseInt(value)
                setReportAttribute(report.report_uuid, "desired_response_times", desiredResponseTimes, reload)
            }}
            type="number"
            value={getDesiredResponseTime(report, status)?.toString()}
        />
    )
}
DesiredResponseTimeInput.propTypes = {
    reload: func,
    report: reportPropType,
    status: oneOfType([statusPropType, entityStatusPropType]),
}

export function ReactionTimes(props) {
    return (
        <Grid container alignItems="flex-start" spacing={{ xs: 1, sm: 2, md: 2 }} columns={{ xs: 1, sm: 2, md: 4 }}>
            <Grid size={{ xs: 1, sm: 2, md: 4 }}>
                <Typography>Desired metric response times</Typography>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="unknown" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="target_not_met" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="near_target_met" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput hoverableLabel status="debt_target_met" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 4 }}>
                <Typography>
                    Desired time after which to review measurement entities (violations, warnings, issues, etc.)
                </Typography>
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="confirmed" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="fixed" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="false_positive" {...props} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <DesiredResponseTimeInput status="wont_fix" {...props} />
            </Grid>
        </Grid>
    )
}
ReactionTimes.propTypes = {
    reload: func,
    report: reportPropType,
}
