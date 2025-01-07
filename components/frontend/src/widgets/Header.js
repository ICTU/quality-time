import { Stack, Typography } from "@mui/material"
import { element, oneOfType, string } from "prop-types"

export function Header({ header, level, subheader }) {
    return (
        <Stack direction="column" sx={{ whiteSpace: "normal" }}>
            <Typography variant={level}>{header}</Typography>
            <Typography variant={`h${parseInt(level[1]) + 1}`}>{subheader}</Typography>
        </Stack>
    )
}
Header.propTypes = {
    header: oneOfType([element, string]),
    level: string,
    subheader: oneOfType([element, string]),
}
