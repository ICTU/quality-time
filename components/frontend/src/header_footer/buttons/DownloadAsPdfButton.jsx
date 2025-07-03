import PictureAsPdf from "@mui/icons-material/PictureAsPdf"
import { string } from "prop-types"
import { useState } from "react"

import { getReportPdf } from "../../api/report"
import { registeredURLSearchParams } from "../../hooks/url_search_query"
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
                let url = window.URL.createObjectURL(response)
                let a = document.createElement("a")
                a.href = url
                const now = new Date()
                const localNow = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
                a.download = `Quality-time-${reportId}-${localNow.toISOString().split(".")[0]}.pdf`
                a.click()
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
        window.location.origin + window.location.pathname + "?" + query.toString() + window.location.hash,
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
