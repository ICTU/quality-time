import { bool } from "prop-types"

import {
    popupContentPropType,
    settingsPropType,
    sortDirectionPropType,
    sortDirectionURLSearchQueryPropType,
} from "../../sharedPropTypes"
import { capitalize } from "../../utils"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function DateOrderMenu({ settings }) {
    const sortOrderMenuItemProps = {
        disabled: settings.nrDates.equals(1),
        help: "The date order can only be changed when at least two dates are shown",
        sortOrder: settings.dateOrder,
    }
    return (
        <SettingsMenu title="Date order">
            <SortOrderMenuItem order="ascending" {...sortOrderMenuItemProps} />
            <SortOrderMenuItem order="descending" {...sortOrderMenuItemProps} />
        </SettingsMenu>
    )
}
DateOrderMenu.propTypes = {
    settings: settingsPropType,
}

function SortOrderMenuItem({ disabled, order, sortOrder, help }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : sortOrder.equals(order)}
            disabled={disabled}
            disabledHelp={help}
            onClick={sortOrder.set}
            onClickData={order}
        >
            {capitalize(order)}
        </SettingsMenuItem>
    )
}
SortOrderMenuItem.propTypes = {
    disabled: bool,
    order: sortDirectionPropType,
    sortOrder: sortDirectionURLSearchQueryPropType,
    help: popupContentPropType,
}
