import Grid from "@mui/material/Grid"
import { func } from "prop-types"
import { useContext } from "react"

import { setReportAttribute } from "../api/report"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { CommentField } from "../fields/CommentField"
import { TextField } from "../fields/TextField"
import { reportPropType } from "../sharedPropTypes"

export function ReportConfiguration({ reload, report }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <Grid container alignItems="flex-end" spacing={{ xs: 1, sm: 1, md: 2 }} columns={{ xs: 1, sm: 2, md: 2 }}>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="report_title"
                    label="Report title"
                    onChange={(value) => setReportAttribute(report.report_uuid, "title", value, reload)}
                    value={report.title}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 1, md: 1 }}>
                <TextField
                    disabled={disabled}
                    id="report-subtitle"
                    label="Report subtitle"
                    onChange={(value) => setReportAttribute(report.report_uuid, "subtitle", value, reload)}
                    value={report.subtitle}
                />
            </Grid>
            <Grid size={{ xs: 1, sm: 2, md: 2 }}>
                <CommentField
                    disabled={disabled}
                    id="report-comment"
                    onChange={(value) => setReportAttribute(report.report_uuid, "comment", value, reload)}
                    value={report.comment}
                />
            </Grid>
        </Grid>
    )
}
ReportConfiguration.propTypes = {
    reload: func,
    report: reportPropType,
}
