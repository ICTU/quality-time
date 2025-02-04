import { Box } from "@mui/material"
import { element, number } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"

export function ButtonRow({ children, rightButton, paddingBottom, paddingLeft, paddingRight, paddingTop }) {
    return (
        <Box
            sx={{
                display: "flex",
                justifyContent: "space-between",
                padding: 1,
                paddingBottom: paddingBottom,
                paddingLeft: paddingLeft,
                paddingRight: paddingRight,
                paddingTop: paddingTop,
            }}
        >
            <Box sx={{ display: "flex", columnGap: 1 }}>{children}</Box>
            {rightButton}
        </Box>
    )
}
ButtonRow.propTypes = {
    children: childrenPropType,
    rightButton: element,
    paddingBottom: number,
    paddingLeft: number,
    paddingRight: number,
    paddingTop: number,
}
