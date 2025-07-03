import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import ArrowRightIcon from "@mui/icons-material/ArrowRight"
import { bool, func } from "prop-types"

import { AppBarButton } from "./AppBarbutton"

export function SettingsButton({ isSettingsPanelVisible, setIsSettingsPanelVisible }) {
    return (
        <AppBarButton
            tooltip="Hide or show cards, columns, metrics, tags, and issue details, change sort order of columns"
            startIcon={isSettingsPanelVisible ? <ArrowDropDownIcon /> : <ArrowRightIcon />}
            onClick={() => setIsSettingsPanelVisible(!isSettingsPanelVisible)}
        >
            Settings
        </AppBarButton>
    )
}
SettingsButton.propTypes = {
    isSettingsPanelVisible: bool,
    setIsSettingsPanelVisible: func,
}
