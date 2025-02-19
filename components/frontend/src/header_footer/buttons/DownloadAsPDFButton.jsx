import PictureAsPdf from "@mui/icons-material/PictureAsPdf"
import { string } from "prop-types"
import { useState } from "react"

import { get_report_pdf } from "../../api/report"
import { registeredURLSearchParams } from "../../hooks/url_search_query"
import { showMessage } from "../../widgets/toast"

import { AppBarButton } from "./AppBarbutton"

function downloadPDF(report_uuid, queryString, callback) {
    const reportId = report_uuid ? `report-${report_uuid}` : "reports-overview"
    return get_report_pdf(report_uuid, queryString)
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
                const local_now = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
                a.download = `Quality-time-${reportId}-${local_now.toISOString().split(".")[0]}.pdf`
                a.click()
            }
            return null
        })
        .catch((error) => showMessage("error", "Could not fetch PDF report", `${error}`))
        .finally(() => callback())
}

export function DownloadAsPDFButton({ report_uuid }) {
    const [loading, setLoading] = useState(false)
    // Make sure the report_url contains only registered query parameters
    const query = registeredURLSearchParams()
    const queryString = query.toString() ? "?" + query.toString() : ""
    query.set("report_url", window.location.origin + window.location.pathname + queryString + window.location.hash)
    const itemType = report_uuid ? "report" : "reports overview"
    return (
        <AppBarButton
            loading={loading}
            onClick={() => {
                setLoading(true)
                downloadPDF(report_uuid, `?${query.toString()}`, () => {
                    setLoading(false)
                })
            }}
            startIcon={<PictureAsPdf />}
            tooltip={`Generate a PDF version of the ${itemType} as currently displayed. This may take some time.`}
        >
            Download as PDF
        </AppBarButton>
    )
}
DownloadAsPDFButton.propTypes = {
    report_uuid: string,
}
