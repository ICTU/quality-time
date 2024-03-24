import { toast } from "react-toastify"
import { registeredURLSearchParams } from "../hooks/url_search_query"

export function showMessage(type, title, description, messageId) {
    const hideToasts = registeredURLSearchParams().get("hide_toasts")
    if (hideToasts !== "true") {
        const toastMessage =
            title && description ? (
                <>
                    <h4>{title}</h4>
                    <p>{description}</p>
                </>
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
    json.availability?.forEach(({ status_code, reason }) => {
        if (status_code === 200) {
            showMessage("success", "URL connection OK")
        } else {
            const status_code_text =
                status_code >= 0 ? "[HTTP status code " + status_code + "] " : ""
            showMessage("warning", "URL connection error", status_code_text + reason)
        }
    })
}
