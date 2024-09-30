import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import ArrowRightIcon from "@mui/icons-material/ArrowRight"
import { Button } from "@mui/material"
import { bool, func } from "prop-types"

export function SettingsButton({ settingsPanelVisible, setSettingsPanelVisible }) {
    return (
        <Button
            color="inherit"
            startIcon={settingsPanelVisible ? <ArrowDropDownIcon /> : <ArrowRightIcon />}
            onClick={() => setSettingsPanelVisible(!settingsPanelVisible)}
        >
            Settings
        </Button>
    )
}
SettingsButton.propTypes = {
    settingsPanelVisible: bool,
    setSettingsPanelVisible: func,
}
