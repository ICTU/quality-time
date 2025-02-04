import SettingsBackupRestoreIcon from "@mui/icons-material/SettingsBackupRestore"
import { Button, Tooltip } from "@mui/material"
import { bool, func } from "prop-types"

import { optionalDatePropType, settingsPropType } from "../../sharedPropTypes"

export function ResetSettingsButton({ atReportsOverview, handleDateChange, reportDate, settings }) {
    const label = `Reset ${atReportsOverview ? "reports overview" : "this report's"} settings`
    return (
        <Tooltip title={label}>
            <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                <Button
                    color="inherit"
                    disabled={settings.allDefault() && reportDate === null}
                    startIcon={<SettingsBackupRestoreIcon />}
                    onClick={() => {
                        handleDateChange(null)
                        settings.reset()
                    }}
                    sx={{ height: "100%" }}
                >
                    Reset settings
                </Button>
            </span>
        </Tooltip>
    )
}
ResetSettingsButton.propTypes = {
    atReportsOverview: bool,
    handleDateChange: func,
    reportDate: optionalDatePropType,
    settings: settingsPropType,
}
