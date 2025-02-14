import { IconButton } from "@mui/material"
import { bool, func } from "prop-types"

import { CaretDown, CaretRight } from "../icons"

export function ExpandButton({ expand, onClick }) {
    return (
        <IconButton aria-label="Expand/collapse" onClick={onClick}>
            {expand ? <CaretDown size="1.5em" /> : <CaretRight size="1.5em" />}
        </IconButton>
    )
}
ExpandButton.propTypes = {
    expand: bool,
    onClick: func,
}
