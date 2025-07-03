import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import ArrowRightIcon from "@mui/icons-material/ArrowRight"
import EventIcon from "@mui/icons-material/Event"
import { Stack } from "@mui/material"
import { bool, func } from "prop-types"

import { datePropType } from "../../sharedPropTypes"
import { AppBarButton } from "./AppBarbutton"

export function ReportPeriodButton({ reportDate, setIsSettingsPanelVisible, isSettingsPanelVisible }) {
    return (
        <AppBarButton
            tooltip="Change report date, number of dates shown, time between dates, and date order"
            startIcon={
                <Stack direction="row" spacing={0}>
                    {isSettingsPanelVisible ? <ArrowDropDownIcon /> : <ArrowRightIcon />}
                    <EventIcon />
                </Stack>
            }
            onClick={() => setIsSettingsPanelVisible(!isSettingsPanelVisible)}
        >
            {reportDate ? reportDate.toLocaleDateString() : "today"}
        </AppBarButton>
    )
}
ReportPeriodButton.propTypes = {
    reportDate: datePropType,
    setIsSettingsPanelVisible: func,
    isSettingsPanelVisible: bool,
}
