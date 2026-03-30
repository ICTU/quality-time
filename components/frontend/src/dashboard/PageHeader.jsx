import { Stack, Typography } from "@mui/material"
import { useState } from "react"

import { useLanguageURLSearchQuery } from "../app_ui_settings"
import { formatDate, formatTime } from "../datetime"
import { datePropType, reportPropType } from "../sharedPropTypes"
import { HyperLink } from "../widgets/HyperLink"

export function PageHeader({ lastUpdate, report, reportDate }) {
    const [now] = useState(() => new Date())
    const language = useLanguageURLSearchQuery().value
    const reportURL = new URLSearchParams(globalThis.location.search).get("report_url") ?? globalThis.location.href
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
            <Typography key={"date"}>{"Report date: " + formatDate(reportDate ?? now, language)}</Typography>
            <Typography key={"generated"}>
                {"Generated: " + formatDate(lastUpdate, language) + ", " + formatTime(lastUpdate, language)}
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
