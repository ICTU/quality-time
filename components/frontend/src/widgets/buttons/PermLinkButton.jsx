import { Button, Tooltip } from "@mui/material"
import { string } from "prop-types"

import { OpenLink } from "../icons"
import { showMessage } from "../toast"

export function PermLinkButton({ itemType, url }) {
    if (globalThis.isSecureContext) {
        // Frontend runs in a secure context (https) so we can use the Clipboard API
        return (
            <Tooltip title={`Copy a permanent link to this ${itemType} to the clipboard`}>
                <Button
                    onClick={() =>
                        navigator.clipboard
                            .writeText(url)
                            .then(() => showMessage("success", "Copied URL to clipboard"))
                            .catch((error) => showMessage("error", "Could not copy URL to clipboard", `${error}`))
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
