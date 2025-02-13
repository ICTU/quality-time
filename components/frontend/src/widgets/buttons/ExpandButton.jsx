import { IconButton } from "@mui/material"
import { bool, func } from "prop-types"

import { CaretDown, CaretRight } from "../icons"

export function ExpandButton({ expand, onClick }) {
    return (
        <IconButton aria-label="Expand/collapse" onClick={onClick}>
            {expand ? <CaretDown /> : <CaretRight />}
        </IconButton>
    )
}
ExpandButton.propTypes = {
    expand: bool,
    onClick: func,
}
