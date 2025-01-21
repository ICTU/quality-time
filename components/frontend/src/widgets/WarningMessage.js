import { Alert, AlertTitle } from "@mui/material"
import { bool, string } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"

export function WarningMessage({ children, pre, showIf, title }) {
    // Show a warning message if showIf is true or undefined
    return (showIf ?? true) ? (
        <Alert severity="warning">
            <AlertTitle>{title}</AlertTitle>
            {pre ? <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}>{children}</pre> : children}
        </Alert>
    ) : null
}
WarningMessage.propTypes = {
    children: childrenPropType,
    pre: bool,
    showIf: bool,
    title: string,
}

export function FailedToLoadMeasurementsWarningMessage() {
    return (
        <WarningMessage title="Loading measurements failed">
            Loading the measurements from the API-server failed.
        </WarningMessage>
    )
}

export function InfoMessage({ children, title }) {
    return (
        <Alert severity="info">
            <AlertTitle>{title}</AlertTitle>
            {children}
        </Alert>
    )
}
InfoMessage.propTypes = {
    children: childrenPropType,
    title: string,
}
