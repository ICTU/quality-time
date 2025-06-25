import { IconButton } from "@mui/material"
import { bool, func, string } from "prop-types"

import { CaretDown, CaretRight } from "../icons"

export function ExpandButton({ expand, onClick, size }) {
    return (
        <IconButton
            aria-label="Expand/collapse"
            onClick={onClick}
            sx={{
                "@media print": {
                    display: "none !important",
                },
                marginLeft: "-0.5rem",
            }}
        >
            {expand ? <CaretDown size={size ?? "1.5em"} /> : <CaretRight size={size ?? "1.5em"} />}
        </IconButton>
    )
}
ExpandButton.propTypes = {
    expand: bool,
    onClick: func,
    size: string,
}
