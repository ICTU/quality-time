import Grid from "@mui/material/Grid2"
import { bool, object, oneOfType, string } from "prop-types"

import { WarningMessage } from "./WarningMessage"

export function ErrorMessage({ formatAsText, message, title }) {
    return (
        <Grid size={{ xs: 1, sm: 2, md: 2 }}>
            <WarningMessage title={title}>
                {formatAsText ? (
                    message
                ) : (
                    <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}>{message}</pre>
                )}
            </WarningMessage>
        </Grid>
    )
}
ErrorMessage.propTypes = {
    formatAsText: bool,
    message: oneOfType([object, string]),
    title: string,
}
