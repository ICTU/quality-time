import { Button, Tooltip } from "@mui/material"
import { string } from "prop-types"
import { useContext, useRef } from "react"

import { SnackbarContext } from "../../context/Snackbar"
import { OpenLink } from "../icons"

export function PermLinkButton({ itemType, url }) {
    const showMessageRef = useRef(useContext(SnackbarContext))
    if (globalThis.isSecureContext) {
        // Frontend runs in a secure context (https) so we can use the Clipboard API
        return (
            <Tooltip title={`Copy a permanent link to this ${itemType} to the clipboard`}>
                <Button
                    onClick={() =>
                        navigator.clipboard
                            .writeText(url)
                            .then(() =>
                                showMessageRef.current({ severity: "success", title: "Copied URL to clipboard" }),
                            )
                            .catch((error) =>
                                showMessageRef.current({
                                    severity: "error",
                                    title: "Could not copy URL to clipboard",
                                    description: `${error}`,
                                }),
                            )
                    }
                    startIcon={<OpenLink />}
                    variant="outlined"
                >
                    {`Share ${itemType}`}
                </Button>
            </Tooltip>
        )
    }
    return null
}
PermLinkButton.propTypes = {
    itemType: string,
    url: string,
}
