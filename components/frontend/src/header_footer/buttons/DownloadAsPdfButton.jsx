import PictureAsPdf from "@mui/icons-material/PictureAsPdf"
import { string } from "prop-types"
import { useState } from "react"

import { getReportPdf } from "../../api/report"
import { registeredURLSearchParams } from "../../hooks/url_search_query"
import { localTimestamp, triggerDownload } from "../../widgets/download"
import { showMessage } from "../../widgets/toast"
import { AppBarButton } from "./AppBarbutton"

function downloadPdf(reportUuid, queryString, callback) {
    const reportId = reportUuid ? `report-${reportUuid}` : "reports-overview"
    return getReportPdf(reportUuid, queryString)
        .then((response) => {
            if (response.ok === false) {
                showMessage(
                    "error",
                    "PDF rendering failed",
                    "HTTP code " + response.status + ": " + response.statusText,
                )
            } else {
                triggerDownload(response, `Quality-time-${reportId}-${localTimestamp()}.pdf`)
            }
            return null
        })
        .catch((error) => showMessage("error", "Could not fetch PDF report", `${error}`))
        .finally(() => callback())
}

export function DownloadAsPdfButton({ reportUuid }) {
    const [loading, setLoading] = useState(false)
    // Make sure the report_url contains only registered query parameters
    const query = registeredURLSearchParams()
    query.set("language", navigator.language)
    query.set(
        "report_url",
        globalThis.location.origin + globalThis.location.pathname + "?" + query.toString() + globalThis.location.hash,
    )
    const itemType = reportUuid ? "report" : "reports overview"
    return (
        <AppBarButton
            loading={loading}
            onClick={() => {
                setLoading(true)
                downloadPdf(reportUuid, `?${query.toString()}`, () => {
                    setLoading(false)
                })
            }}
            startIcon={<PictureAsPdf />}
            tooltip={`Generate a PDF version of the ${itemType} as currently displayed—this may take a few seconds`}
        >
            Download as PDF
        </AppBarButton>
    )
}
DownloadAsPdfButton.propTypes = {
    reportUuid: string,
}
