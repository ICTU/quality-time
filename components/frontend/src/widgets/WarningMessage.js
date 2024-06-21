import { bool } from "prop-types"

import { Message } from "../semantic_ui_react_wrappers"

export function WarningMessage(props) {
    // Show a warning message if showIf is true
    const { showIf, ...messageProps } = props
    return showIf ? <Message warning {...messageProps} /> : null
}
WarningMessage.propTypes = {
    showIf: bool,
}
