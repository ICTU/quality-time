import { Alert, AlertTitle, LinearProgress, Snackbar, Stack } from "@mui/material"
import { func, number } from "prop-types"
import { useEffect, useRef, useState } from "react"

import { SnackbarContext } from "../context/Snackbar"
import { registeredURLSearchParams } from "../hooks/url_search_query"
import { childrenPropType, snackbarMessagePropType, snackbarMessagesPropType } from "../sharedPropTypes"

export function SnackbarAlerts({ children, messages, hideMessage, showMessage }) {
    return (
        <>
            {messages.map((message, index) => (
                <SnackbarAlert
                    key={JSON.stringify(message)}
                    index={index}
                    message={message}
                    hideMessage={hideMessage}
                />
            ))}
            <SnackbarContext value={showMessage}>{children}</SnackbarContext>
        </>
    )
}
SnackbarAlerts.propTypes = {
    children: childrenPropType,
    hideMessage: func,
    messages: snackbarMessagesPropType,
    showMessage: func,
}

const AUTO_HIDE_DURATION_MS = 20_000
const PROGRESS_BAR_STEP_MS = 250

function SnackbarAlert({ index, message, hideMessage }) {
    const [progress, setProgress] = useState(0)
    const hoverRef = useRef(false)

    useEffect(() => {
        const timer = setInterval(() => {
            if (!hoverRef.current) {
                setProgress((oldProgress) => oldProgress + PROGRESS_BAR_STEP_MS)
            }
        }, PROGRESS_BAR_STEP_MS)
        return () => clearInterval(timer)
    }, [])

    useEffect(() => {
        if (progress > AUTO_HIDE_DURATION_MS) {
            hideMessage(message)
        }
    }, [progress, hideMessage, message])

    if (progress > AUTO_HIDE_DURATION_MS || registeredURLSearchParams().get("hide_toasts") === "true") {
        return null
    }
    return (
        <Snackbar
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            message={message}
            open={true}
            onMouseEnter={() => {
                hoverRef.current = true
            }}
            onMouseLeave={() => {
                hoverRef.current = false
            }}
            sx={{ bottom: { sm: 20 + 100 * index } }}
            slotProps={{
                clickAwayListener: {
                    onClickAway: (event) => {
                        event.defaultMuiPrevented = true // Prevent default 'onClickAway' behavior.
                    },
                },
            }}
        >
            <Alert
                severity={message.severity}
                onClose={() => hideMessage(message)}
                sx={{ width: "100%" }}
                variant="filled"
            >
                <Stack spacing={1}>
                    <AlertTitle>{message.title}</AlertTitle>
                    {message.description}
                    <LinearProgress
                        aria-label="Seconds left until hiding notification"
                        color={message.severity}
                        value={Math.min(100, (100 * progress) / AUTO_HIDE_DURATION_MS)}
                        variant="determinate"
                    />
                </Stack>
            </Alert>
        </Snackbar>
    )
}
SnackbarAlert.propTypes = {
    hideMessage: func.isRequired,
    index: number.isRequired,
    message: snackbarMessagePropType.isRequired,
}
