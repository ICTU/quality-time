import DownloadIcon from "@mui/icons-material/Download"
import { Button, Tooltip } from "@mui/material"
import { string } from "prop-types"
import { useState } from "react"

import { exportReport } from "../../api/report"
import { localTimestamp, triggerDownload } from "../download"
import { showMessage } from "../toast"

function downloadJson(reportUuid, callback) {
    return exportReport(reportUuid)
        .then((response) => {
            if (response.ok === false) {
                showMessage("error", "Export failed", "HTTP code " + response.status + ": " + response.statusText)
            } else {
                const blob = new Blob([JSON.stringify(response, null, 2)], { type: "application/json" })
                triggerDownload(blob, `Quality-time-report-${reportUuid}-${localTimestamp()}.json`)
            }
            return null
        })
        .catch((error) => showMessage("error", "Could not export report", `${error}`))
        .finally(() => callback())
}

export function ExportReportButton({ reportUuid }) {
    const [loading, setLoading] = useState(false)
    return (
        <Tooltip title="Export this report to a JSON file. Note that measurements are not included and that source credentials are encrypted with the public key of this Quality-time instance.">
            <Button
                disabled={loading}
                onClick={() => {
                    setLoading(true)
                    downloadJson(reportUuid, () => {
                        setLoading(false)
                    })
                }}
                startIcon={<DownloadIcon />}
                variant="outlined"
            >
                {"Export report"}
            </Button>
        </Tooltip>
    )
}
ExportReportButton.propTypes = {
    reportUuid: string,
}
