import { MenuItem } from "@mui/material"
import Grid from "@mui/material/Grid"
import { DatePicker } from "@mui/x-date-pickers/DatePicker"
import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import { func, string } from "prop-types"
import { useContext } from "react"

import { setMetricAttribute, setMetricDebt } from "../api/metric"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { CommentField } from "../fields/CommentField"
import { TextField } from "../fields/TextField"
import { IssuesRows } from "../issue/IssuesRows"
import { metricPropType, reportPropType } from "../sharedPropTypes"
import { HyperLink } from "../widgets/HyperLink"
import { Target } from "./Target"

dayjs.extend(relativeTime)

function AcceptTechnicalDebt({ metric, metricUuid, reload }) {
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
                    setMetricDebt(metricUuid, acceptDebt, reload)
                } else {
                    setMetricAttribute(metricUuid, "accept_debt", acceptDebt, reload)
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
    metricUuid: string,
    reload: func,
}

function TechnicalDebtEndDate({ metric, metricUuid, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const debtEndDateTime = metric.debt_end_date ? dayjs(metric.debt_end_date) : null
    const helperText = metric.debt_end_date
        ? debtEndDateTime.fromNow()
        : "Accept technical debt until this date. After this date, or when the issues below have all been resolved, whichever happens first, the technical debt should be resolved and the technical debt target is no longer evaluated."
    return (
        <DatePicker
            defaultValue={debtEndDateTime}
            disabled={disabled}
            label="Technical debt end date"
            onChange={(value) => setMetricAttribute(metricUuid, "debt_end_date", value, reload)}
            slotProps={{ field: { clearable: true }, textField: { helperText: helperText } }}
            sx={{ width: "100%" }}
            timezone="default"
        />
    )
}
TechnicalDebtEndDate.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
}

export function MetricDebtParameters({ metric, metricUuid, reload, report }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <Grid alignItems="flex-start" container spacing={{ xs: 1, sm: 2, md: 3 }} columns={{ xs: 1, sm: 3, md: 6 }}>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <AcceptTechnicalDebt metric={metric} metricUuid={metricUuid} reload={reload} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <Target targetType="debt_target" metric={metric} metricUuid={metricUuid} reload={reload} />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 2 }}>
                <TechnicalDebtEndDate metric={metric} metricUuid={metricUuid} reload={reload} />
            </Grid>
            <IssuesRows metric={metric} metricUuid={metricUuid} reload={reload} report={report} />
            <Grid size={{ xs: 1, sm: 3, md: 6 }}>
                <CommentField
                    disabled={disabled}
                    onChange={(value) => setMetricAttribute(metricUuid, "comment", value, reload)}
                    value={metric.comment}
                />
            </Grid>
        </Grid>
    )
}
MetricDebtParameters.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
    report: reportPropType,
}
