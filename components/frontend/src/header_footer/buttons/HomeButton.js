import { Button, Tooltip, Typography } from "@mui/material"
import { bool, func } from "prop-types"

export function HomeButton({ atReportsOverview, openReportsOverview, setSettingsPanelVisible }) {
    const label = "Go to reports overview"
    return (
        <Tooltip title={label}>
            <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                <Button
                    color="inherit"
                    disabled={atReportsOverview}
                    onClick={() => {
                        setSettingsPanelVisible(false)
                        openReportsOverview()
                    }}
                    startIcon={<img height="28px" width="28px" src="/favicon.ico" alt={label} />}
                    sx={{ textTransform: "none" }}
                >
                    <Typography variant="h4">Quality-time</Typography>
                </Button>
            </span>
        </Tooltip>
    )
}
HomeButton.propTypes = {
    atReportsOverview: bool,
    openReportsOverview: func,
    setSettingsPanelVisible: func,
}
