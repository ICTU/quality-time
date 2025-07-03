import { Stack, Typography } from "@mui/material"
import { StaticDatePicker } from "@mui/x-date-pickers/StaticDatePicker"
import dayjs from "dayjs"
import { date, func } from "prop-types"

import { settingsPropType } from "../sharedPropTypes"
import { DateOrderMenu } from "./settings_menu/DateOrderMenu"
import { NumberOfDatesMenu } from "./settings_menu/NumberOfDatesMenu"
import { SettingsMenuGroup } from "./settings_menu/SettingsMenu"
import { TimeBetweenDatesMenu } from "./settings_menu/TimeBetweenDatesMenu"

export function ReportPeriodPanel({ onChange, reportDate, settings }) {
    return (
        <SettingsMenuGroup justify="right">
            <NumberOfDatesMenu settings={settings} />
            <TimeBetweenDatesMenu settings={settings} />
            <DateOrderMenu settings={settings} />
            <Stack>
                <Typography variant="h3" noWrap>
                    Report date
                </Typography>
                <StaticDatePicker
                    disableFuture
                    onChange={(date) => onChange(date.$d)}
                    slots={{ toolbar: null }}
                    slotProps={{
                        actionBar: { actions: ["today"] },
                        layout: { sx: { backgroundColor: "rgb(0,0,0,0)" } }, // Make the background transparent
                    }}
                    value={dayjs(reportDate)}
                />
            </Stack>
        </SettingsMenuGroup>
    )
}
ReportPeriodPanel.propTypes = {
    onChange: func,
    reportDate: date,
    settings: settingsPropType,
}
