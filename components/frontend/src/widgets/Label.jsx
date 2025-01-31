import { Box } from "@mui/material"
import { string } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"

export function Label({ color, children }) {
    const bgcolor = `${color}.dark`
    const fgcolor = `${color}.contrastText`
    return (
        <Box
            className={color}
            sx={{
                bgcolor: bgcolor,
                color: fgcolor,
                display: "inline-flex",
                margin: "1px",
                borderRadius: "4px",
                padding: "4px",
            }}
        >
            {children}
        </Box>
    )
}
Label.propTypes = {
    color: string,
    children: childrenPropType,
}
