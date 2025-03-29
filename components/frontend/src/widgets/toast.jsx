import { toast } from "react-toastify"

import { registeredURLSearchParams } from "../hooks/url_search_query"

export function showMessage(type, title, description, messageId) {
    const hideToasts = registeredURLSearchParams().get("hide_toasts")
    if (hideToasts !== "true") {
        const toastMessage =
            title && description ? (
                <div>
                    <b>{title}</b>
                    <p>{description}</p>
                </div>
            ) : (
                title
            )
        const options = { type: type, autoClose: 20000 }
        if (messageId) {
            options["toastId"] = messageId
        }
        toast(toastMessage, options)
    }
}

export function showConnectionMessage(json) {
    json.availability?.forEach(({ status_code: statusCode, reason }) => {
        if (statusCode === 200) {
            showMessage("success", "URL connection OK")
        } else {
            const statusCodeText = statusCode >= 0 ? "[HTTP status code " + statusCode + "] " : ""
            showMessage("warning", "URL connection error", statusCodeText + reason)
        }
    })
}
