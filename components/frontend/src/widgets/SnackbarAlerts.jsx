import { Alert, AlertTitle, LinearProgress, Snackbar, Stack } from "@mui/material"
import { func, number } from "prop-types"
import { useEffect, useState } from "react"

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

function SnackbarAlert({ index, message, hideMessage }) {
    const [progress, setProgress] = useState(0)
    const [hover, setHover] = useState(false)
    const autoHideDuration = 20000
    const step = 250

    useEffect(() => {
        const timer = setInterval(() => {
            if (!hover) {
                setProgress((oldProgress) => oldProgress + step)
            }
        }, step)
        return () => clearInterval(timer)
    }, [hover])

    useEffect(() => {
        if (progress > autoHideDuration) {
            hideMessage(message)
        }
    }, [progress, hideMessage, message])

    if (progress > autoHideDuration || registeredURLSearchParams().get("hide_toasts") === "true") {
        return null
    }
    return (
        <Snackbar
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
            message={message}
            open={true}
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
            resumeHideDuration={autoHideDuration - progress}
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
                        value={Math.min(100, (100 * progress) / autoHideDuration)}
                        variant="determinate"
                    />
                </Stack>
            </Alert>
        </Snackbar>
    )
}
SnackbarAlert.propTypes = {
    hideMessage: func,
    index: number,
    message: snackbarMessagePropType,
}
