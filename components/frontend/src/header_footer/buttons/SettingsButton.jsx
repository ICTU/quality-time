import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import ArrowRightIcon from "@mui/icons-material/ArrowRight"
import { bool, func } from "prop-types"

import { AppBarButton } from "./AppBarbutton"

export function SettingsButton({ settingsPanelVisible, setSettingsPanelVisible }) {
    return (
        <AppBarButton
            startIcon={settingsPanelVisible ? <ArrowDropDownIcon /> : <ArrowRightIcon />}
            onClick={() => setSettingsPanelVisible(!settingsPanelVisible)}
        >
            Settings
        </AppBarButton>
    )
}
SettingsButton.propTypes = {
    settingsPanelVisible: bool,
    setSettingsPanelVisible: func,
}
