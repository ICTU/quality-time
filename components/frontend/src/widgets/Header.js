import { Typography } from "@mui/material"
import { element, oneOfType, string } from "prop-types"

export function Header({ header, level, subheader }) {
    return (
        <div>
            <Typography variant={level}>{header}</Typography>
            <Typography variant={`h${parseInt(level[1]) + 1}`} sx={{ color: "text.secondary" }}>
                {subheader}
            </Typography>
        </div>
    )
}
Header.propTypes = {
    header: oneOfType([element, string]),
    level: string,
    subheader: oneOfType([element, string]),
}
