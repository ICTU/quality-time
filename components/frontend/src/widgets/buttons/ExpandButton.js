import { IconButton } from "@mui/material"
import { bool, func, string } from "prop-types"

import { CaretDown, CaretRight } from "../icons"

export function ExpandButton({ expand, onClick, size }) {
    return (
        <IconButton aria-label="Expand/collapse" onClick={onClick}>
            {expand ? <CaretDown size={size} /> : <CaretRight size={size} />}
        </IconButton>
    )
}
ExpandButton.propTypes = {
    expand: bool,
    onClick: func,
    size: string,
}
