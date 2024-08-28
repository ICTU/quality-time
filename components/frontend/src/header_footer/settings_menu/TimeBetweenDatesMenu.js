import { bool, number } from "prop-types"

import { integerURLSearchQueryPropType, popupContentPropType, settingsPropType } from "../../sharedPropTypes"
import { pluralize } from "../../utils"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function TimeBetweenDatesMenu({ settings }) {
    const dateIntervalMenuItemProps = {
        dateInterval: settings.dateInterval,
        disabled: settings.nrDates.equals(1),
        help: "The date interval can only be changed when at least two dates are shown",
    }
    return (
        <SettingsMenu title="Time between dates">
            <DateIntervalMenuItem key={1} nr={1} {...dateIntervalMenuItemProps} />
            {[7, 14, 21, 28].map((nr) => (
                <DateIntervalMenuItem key={nr} nr={nr} {...dateIntervalMenuItemProps} />
            ))}
        </SettingsMenu>
    )
}
TimeBetweenDatesMenu.propTypes = {
    settings: settingsPropType,
}

function DateIntervalMenuItem({ nr, dateInterval, disabled, help }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : dateInterval.equals(nr)}
            disabled={disabled}
            disabledHelp={help}
            onClick={dateInterval.set}
            onClickData={nr}
        >
            {nr === 1 ? "1 day" : `${nr / 7} ${pluralize("week", nr / 7)}`}
        </SettingsMenuItem>
    )
}
DateIntervalMenuItem.propTypes = {
    nr: number,
    dateInterval: integerURLSearchQueryPropType,
    disabled: bool,
    help: popupContentPropType,
}
