import { number } from "prop-types"

import { integerURLSearchQueryPropType, settingsPropType } from "../../sharedPropTypes"
import { pluralize } from "../../utils"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function NumberOfDatesMenu({ settings }) {
    return (
        <SettingsMenu title="Number of dates">
            {[1, 2, 3, 4, 5, 6, 7].map((nr) => (
                <NrOfDatesMenuItem key={nr} nr={nr} nrDates={settings.nrDates} />
            ))}
        </SettingsMenu>
    )
}
NumberOfDatesMenu.propTypes = {
    settings: settingsPropType,
}

function NrOfDatesMenuItem({ nr, nrDates }) {
    return (
        <SettingsMenuItem active={nrDates.equals(nr)} onClick={nrDates.set} onClickData={nr}>
            {`${nr} ${pluralize("date", nr)}`}
        </SettingsMenuItem>
    )
}
NrOfDatesMenuItem.propTypes = {
    nr: number,
    nrDates: integerURLSearchQueryPropType,
}
