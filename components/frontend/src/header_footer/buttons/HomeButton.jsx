import { Typography } from "@mui/material"
import { bool, func } from "prop-types"

import { AppBarButton } from "./AppBarbutton"

export function HomeButton({ atReportsOverview, openReportsOverview }) {
    const label = "Go to reports overview"
    return (
        <AppBarButton
            disabled={atReportsOverview}
            onClick={openReportsOverview}
            startIcon={<img height="28px" width="28px" src="/favicon.ico" alt={label} />}
            sx={{ textTransform: "none" }}
            tooltip={label}
        >
            <Typography variant="h3">Quality-time</Typography>
        </AppBarButton>
    )
}
HomeButton.propTypes = {
    atReportsOverview: bool,
    openReportsOverview: func,
}
