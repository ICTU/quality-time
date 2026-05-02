import { func } from "prop-types"

import { availabilityMessagesPropType } from "./sharedPropTypes"

const OK = { severity: "success", title: "URL connection OK", description: "URL was accessed without errors" }
const NOK = { severity: "warning", title: "URL connection error" }

export function showURLAvailabilityMessages(availability, showMessage) {
    availability?.forEach(({ status_code: statusCode, reason }) => {
        if (statusCode === 200) {
            showMessage(OK)
        } else {
            const statusCodeText = statusCode >= 0 ? "[HTTP status code " + statusCode + "] " : ""
            showMessage({ ...NOK, description: statusCodeText + reason })
        }
    })
}
showURLAvailabilityMessages.propTypes = {
    availability: availabilityMessagesPropType,
    showMessage: func,
}
