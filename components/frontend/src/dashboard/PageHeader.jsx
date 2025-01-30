import { Stack, Typography } from "@mui/material"

import { datePropType, reportPropType } from "../sharedPropTypes"
import { HyperLink } from "../widgets/HyperLink"

export function PageHeader({ lastUpdate, report, reportDate }) {
    const reportURL = new URLSearchParams(window.location.search).get("report_url") ?? window.location.href
    const title = report?.title ?? "Reports overview"
    const changelogURL = `https://quality-time.readthedocs.io/en/v${import.meta.env.VITE_APP_VERSION}/changelog.html`
    return (
        <Stack
            direction="row"
            spacing={2}
            sx={{ display: "none", displayPrint: "inline-flex", justifyContent: "space-between", width: "100%" }}
        >
            <Typography key={"reportURL"} data-testid={"reportUrl"}>
                <HyperLink url={reportURL}>{title}</HyperLink>
            </Typography>
            <Typography key={"date"}>{"Report date: " + formatDate(reportDate ?? new Date())}</Typography>
            <Typography key={"generated"}>
                {"Generated: " + formatDate(lastUpdate) + ", " + formatTime(lastUpdate)}
            </Typography>
            <Typography key={"version"} data-testid={"version"}>
                <HyperLink url={changelogURL}>Quality-time v{import.meta.env.VITE_APP_VERSION}</HyperLink>
            </Typography>
        </Stack>
    )
}
PageHeader.propTypes = {
    lastUpdate: datePropType,
    report: reportPropType,
    reportDate: datePropType,
}

// Hard code en-GB to get European style dates and times. See https://github.com/ICTU/quality-time/issues/8381.

function formatDate(date) {
    return date.toLocaleDateString("en-GB", { year: "numeric", month: "2-digit", day: "2-digit" }).replace(/\//g, "-")
}

function formatTime(date) {
    return date.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })
}
