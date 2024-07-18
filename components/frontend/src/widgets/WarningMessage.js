import { bool } from "prop-types"

import { Message } from "../semantic_ui_react_wrappers"

export function WarningMessage(props) {
    // Show a warning message if showIf is true or undefined
    const { showIf, ...messageProps } = props
    return (showIf ?? true) ? <Message warning {...messageProps} /> : null
}
WarningMessage.propTypes = {
    showIf: bool,
}

export function FailedToLoadMeasurementsWarningMessage() {
    return (
        <WarningMessage
            content="Loading the measurements from the API-server failed."
            header="Loading measurements failed"
        />
    )
}
