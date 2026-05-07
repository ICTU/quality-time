import { func } from "prop-types"

import { availabilityMessagePropType } from "./sharedPropTypes"

const OK = { severity: "success", title: "URL connection OK", description: "URL was accessed without errors" }
const NOK = { severity: "warning", title: "URL connection error" }

export function showURLAvailabilityMessage(availability, showMessage) {
    if (availability?.status_code === undefined) return
    const { status_code: statusCode, reason } = availability
    if (statusCode === 200) {
        showMessage(OK)
    } else {
        const statusCodeText = statusCode >= 0 ? "[HTTP status code " + statusCode + "] " : ""
        showMessage({ ...NOK, description: statusCodeText + reason })
    }
}
showURLAvailabilityMessage.propTypes = {
    availability: availabilityMessagePropType,
    showMessage: func,
}
