import { MenuItem } from "@mui/material"
import Grid from "@mui/material/Grid2"
import { DatePicker } from "@mui/x-date-pickers/DatePicker"
import dayjs from "dayjs"
import { func, string } from "prop-types"
import { useContext } from "react"
import TimeAgo from "react-timeago"

import { set_metric_attribute, set_metric_debt } from "../api/metric"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { CommentField } from "../fields/CommentField"
import { TextField } from "../fields/TextField"
import { IssuesRows } from "../issue/IssuesRows"
import { metricPropType, reportPropType } from "../sharedPropTypes"
import { HyperLink } from "../widgets/HyperLink"
import { Target } from "./Target"

function AcceptTechnicalDebt({ metric, metric_uuid, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <TextField
            disabled={disabled}
            helperText={
                <>
                    Read more about{" "}
                    <HyperLink url="https://en.wikipedia.org/wiki/Technical_debt">technical debt</HyperLink>
                </>
            }
            label="Accept technical debt?"
            onChange={(value) => {
                const acceptDebt = value.startsWith("yes")
                if (value.endsWith("completely")) {
                    set_metric_debt(metric_uuid, acceptDebt, reload)
                } else {
                    set_metric_attribute(metric_uuid, "accept_debt", acceptDebt, reload)
                }
            }}
            select
            value={metric.accept_debt ? "yes" : "no"}
        >
            <MenuItem key="yes" value="yes">
                Yes
            </MenuItem>
            <MenuItem key="yes_completely" value="yes_completely">
                Yes, and also set technical debt target and end date
            </MenuItem>
            <MenuItem key="no" value="no">
                No
            </MenuItem>
            <MenuItem key="no_completely" value="no_completely">
                No, and also clear technical debt target and end date
            </MenuItem>
        </TextField>
    )
}
AcceptTechnicalDebt.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function TechnicalDebtEndDate({ metric, metric_uuid, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const debtEndDateTime = metric.debt_end_date ? dayjs(metric.debt_end_date) : null
    const helperText = metric.debt_end_date ? (
        <TimeAgo date={debtEndDateTime} />
    ) : (
        "Accept technical debt until this date. After this date, or when the issues below have all been resolved, whichever happens first, the technical debt should be resolved and the technical debt target is no longer evaluated."
    )
    return (
        <DatePicker
            defaultValue={debtEndDateTime}
            disabled={disabled}
            label="Technical debt end date"
            onChange={(value) => set_metric_attribute(metric_uuid, "debt_end_date", value, reload)}
            slotProps={{ field: { clearable: true }, textField: { helperText: helperText } }}
            sx={{ width: "100%" }}
            timezone="default"
        />
    )
}
TechnicalDebtEndDate.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

export function MetricDebtParameters({ metric, metric_uuid, reload, report }) {
    return (
        <Grid alignItems="flex-start" container spacing={{ xs: 1, sm: 2, md: 3 }} columns={{ xs: 1, sm: 3, md: 6 }}>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <AcceptTechnicalDebt metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <Target
                    key={metric.debt_target}
                    target_type="debt_target"
                    metric={metric}
                    metric_uuid={metric_uuid}
                    reload={reload}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <TechnicalDebtEndDate metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <IssuesRows metric={metric} metric_uuid={metric_uuid} reload={reload} report={report} />
            <Grid size={{ xs: 1, sm: 3, md: 6 }}>
                <CommentField
                    onChange={(value) => set_metric_attribute(metric_uuid, "comment", value, reload)}
                    value={metric.comment}
                />
            </Grid>
        </Grid>
    )
}
MetricDebtParameters.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    report: reportPropType,
}
