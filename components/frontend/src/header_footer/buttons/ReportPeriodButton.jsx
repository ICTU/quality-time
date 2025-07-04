import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import ArrowRightIcon from "@mui/icons-material/ArrowRight"
import EventIcon from "@mui/icons-material/Event"
import { Stack } from "@mui/material"
import { bool, func } from "prop-types"

import { datePropType } from "../../sharedPropTypes"
import { AppBarButton } from "./AppBarbutton"

export function ReportPeriodButton({ reportDate, setSettingsPanelVisible, settingsPanelVisible }) {
    return (
        <AppBarButton
            tooltip="Report date"
            startIcon={
                <Stack direction="row" spacing={0}>
                    {settingsPanelVisible ? <ArrowDropDownIcon /> : <ArrowRightIcon />}
                    <EventIcon />
                </Stack>
            }
            onClick={() => setSettingsPanelVisible(!settingsPanelVisible)}
        >
            {reportDate ? reportDate.toLocaleDateString() : "today"}
        </AppBarButton>
    )
}
ReportPeriodButton.propTypes = {
    reportDate: datePropType,
    setSettingsPanelVisible: func,
    settingsPanelVisible: bool,
}
