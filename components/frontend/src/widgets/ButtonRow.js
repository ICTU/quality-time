import { Box } from "@mui/material"
import { element } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"

export function ButtonRow({ children, rightButton }) {
    return (
        <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Box sx={{ display: "flex", columnGap: 1 }}>{children}</Box>
            {rightButton}
        </Box>
    )
}
ButtonRow.propTypes = {
    children: childrenPropType,
    rightButton: element,
}
