import DownloadIcon from "@mui/icons-material/Download"
import { Button, Tooltip } from "@mui/material"
import { useContext, useRef } from "react"

import { DataModelContext } from "../../context/DataModel"
import { SnackbarContext } from "../../context/Snackbar"
import { listSeparator, reportToCSV } from "../../report/report_csv"
import { datesPropType, measurementsPropType, reportPropType, settingsPropType } from "../../sharedPropTypes"
import { localTimestamp, triggerDownload } from "../download"

function downloadCsv(report, measurements, dates, settings, dataModel, showMessage) {
    try {
        // Use the list separator of the user's locale as column delimiter, so Excel splits the columns correctly when
        // the file is opened by double-clicking
        const csv = reportToCSV(report, measurements, dates, settings, dataModel, listSeparator(navigator.language))
        // Prefix with a UTF-8 byte order mark so spreadsheet applications read the file as UTF-8
        const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" })
        triggerDownload(blob, `Quality-time-report-${report.report_uuid}-${localTimestamp()}.csv`)
    } catch (error) {
        showMessage({ severity: "error", title: "Could not export report to CSV", description: `${error}` })
    }
}

export function ExportReportCsvButton({ report, measurements, dates, settings }) {
    const dataModel = useContext(DataModelContext)
    const showMessageRef = useRef(useContext(SnackbarContext))
    return (
        <Tooltip title="Export this report to a CSV file, mirroring the report as currently displayed.">
            <Button
                onClick={() => downloadCsv(report, measurements, dates, settings, dataModel, showMessageRef.current)}
                startIcon={<DownloadIcon />}
                variant="outlined"
            >
                {"Export as CSV"}
            </Button>
        </Tooltip>
    )
}
ExportReportCsvButton.propTypes = {
    report: reportPropType,
    measurements: measurementsPropType,
    dates: datesPropType,
    settings: settingsPropType,
}
