import SettingsBackupRestoreIcon from "@mui/icons-material/SettingsBackupRestore"
import { bool, func } from "prop-types"

import { optionalDatePropType, settingsPropType } from "../../sharedPropTypes"

import { AppBarButton } from "./AppBarbutton"

export function ResetSettingsButton({ atReportsOverview, handleDateChange, reportDate, settings }) {
    return (
        <AppBarButton
            disabled={settings.allDefault() && reportDate === null}
            onClick={() => {
                handleDateChange(null)
                settings.reset()
            }}
            startIcon={<SettingsBackupRestoreIcon />}
            tooltip={`Reset ${atReportsOverview ? "reports overview" : "this report's"} settings`}
        >
            Reset settings
        </AppBarButton>
    )
}
ResetSettingsButton.propTypes = {
    atReportsOverview: bool,
    handleDateChange: func,
    reportDate: optionalDatePropType,
    settings: settingsPropType,
}
