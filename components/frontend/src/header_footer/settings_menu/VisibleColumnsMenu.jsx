import Divider from "@mui/material/Divider"
import { bool, string } from "prop-types"

import { popupContentPropType, settingsPropType, stringsURLSearchQueryPropType } from "../../sharedPropTypes"
import { capitalize } from "../../utils"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function VisibleColumnMenu({ settings }) {
    const oneDateColumn = settings.nrDates.equals(1)
    const multipleDateColumns = !oneDateColumn
    const visibleColumnMenuItemProps = { hiddenColumns: settings.hiddenColumns }
    return (
        <SettingsMenu title="Visible columns">
            <VisibleColumnMenuItem
                column="trend"
                disabled={multipleDateColumns}
                help="The trend column can only be made visible when one date is shown"
                {...visibleColumnMenuItemProps}
            />
            <VisibleColumnMenuItem
                column="status"
                disabled={multipleDateColumns}
                help="The status column can only be made visible when one date is shown"
                {...visibleColumnMenuItemProps}
            />
            <VisibleColumnMenuItem
                column="measurement"
                disabled={multipleDateColumns}
                help="The measurement column can only be made visible when one date is shown"
                {...visibleColumnMenuItemProps}
            />
            <VisibleColumnMenuItem
                column="target"
                disabled={multipleDateColumns}
                help="The target column can only be made visible when one date is shown"
                {...visibleColumnMenuItemProps}
            />
            <VisibleColumnMenuItem column="unit" {...visibleColumnMenuItemProps} />
            <VisibleColumnMenuItem column="source" {...visibleColumnMenuItemProps} />
            <VisibleColumnMenuItem column="time_left" {...visibleColumnMenuItemProps} />
            <VisibleColumnMenuItem
                column="delta"
                disabled={oneDateColumn}
                help="The delta column(s) can only be made visible when at least two dates are shown"
                itemText="Delta (𝚫)"
                {...visibleColumnMenuItemProps}
            />
            <VisibleColumnMenuItem
                column="overrun"
                disabled={oneDateColumn}
                help="The overrun column can only be made visible when at least two dates are shown"
                {...visibleColumnMenuItemProps}
            />
            <VisibleColumnMenuItem column="comment" {...visibleColumnMenuItemProps} />
            <VisibleColumnMenuItem column="issues" {...visibleColumnMenuItemProps} />
            <VisibleColumnMenuItem column="tags" {...visibleColumnMenuItemProps} />
            <Divider />
            <SettingsMenuItem
                active={!settings.hideEmptyColumns.value}
                onClick={settings.hideEmptyColumns.set}
                onClickData={!settings.hideEmptyColumns.value}
            >
                Empty columns
            </SettingsMenuItem>
        </SettingsMenu>
    )
}
VisibleColumnMenu.propTypes = {
    settings: settingsPropType,
}

function VisibleColumnMenuItem({ column, disabled, hiddenColumns, help, itemText }) {
    return (
        <SettingsMenuItem
            active={disabled ? false : hiddenColumns.excludes(column)}
            disabled={disabled}
            disabledHelp={help}
            onClick={hiddenColumns.toggle}
            onClickData={column}
        >
            {itemText ?? capitalize(column).replaceAll("_", " ")}
        </SettingsMenuItem>
    )
}
VisibleColumnMenuItem.propTypes = {
    column: string,
    disabled: bool,
    hiddenColumns: stringsURLSearchQueryPropType,
    help: popupContentPropType,
    itemText: string,
}
