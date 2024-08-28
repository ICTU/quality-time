import { bool, func, string } from "prop-types"

import { Icon } from "../../semantic_ui_react_wrappers"
import {
    popupContentPropType,
    settingsPropType,
    sortDirectionURLSearchQueryPropType,
    stringURLSearchQueryPropType,
} from "../../sharedPropTypes"
import { capitalize } from "../../utils"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function SortColumnMenu({ handleSort, settings }) {
    const multipleDateColumns = !settings.nrDates.equals(1)
    const sortColumnMenuItemProps = {
        sortColumn: settings.sortColumn,
        sortDirection: settings.sortDirection,
        handleSort: handleSort,
    }
    return (
        <SettingsMenu title="Sort column">
            <SortColumnMenuItem column="name" {...sortColumnMenuItemProps} />
            <SortColumnMenuItem
                column="status"
                disabled={multipleDateColumns || settings.hiddenColumns.includes("status")}
                help="The status column can only be selected for sorting when it is visible"
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="measurement"
                disabled={multipleDateColumns || settings.hiddenColumns.includes("measurement")}
                help="The measurement column can only be selected for sorting when it is visible"
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="target"
                disabled={multipleDateColumns || settings.hiddenColumns.includes("target")}
                help="The target column can only be selected for sorting when it is visible"
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="unit"
                disabled={settings.hiddenColumns.includes("unit")}
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="source"
                disabled={settings.hiddenColumns.includes("source")}
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="time_left"
                disabled={settings.hiddenColumns.includes("time_left")}
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="overrun"
                disabled={settings.nrDates.equals(1) || settings.hiddenColumns.includes("overrun")}
                help="The overrun column can only be selected for sorting when it is visible"
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="comment"
                disabled={settings.hiddenColumns.includes("comment")}
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="issues"
                disabled={settings.hiddenColumns.includes("issues")}
                {...sortColumnMenuItemProps}
            />
            <SortColumnMenuItem
                column="tags"
                disabled={settings.hiddenColumns.includes("tags")}
                {...sortColumnMenuItemProps}
            />
        </SettingsMenu>
    )
}
SortColumnMenu.propTypes = {
    handleSort: func,
    settings: settingsPropType,
}

function SortColumnMenuItem({ column, disabled, sortColumn, sortDirection, handleSort, help }) {
    let sortIndicator = null
    if (sortColumn.equals(column) && sortDirection.value) {
        // We use a triangle because the sort down and up icons are not at the same height
        const iconDirection = sortDirection.equals("ascending") ? "up" : "down"
        sortIndicator = (
            <Icon disabled={disabled} name={`triangle ${iconDirection}`} aria-label={`sorted ${sortDirection.value}`} />
        )
    }
    return (
        <SettingsMenuItem
            active={disabled ? false : sortColumn === column}
            disabled={disabled}
            disabledHelp={help}
            onClick={handleSort}
            onClickData={column}
        >
            {capitalize(column === "name" ? "metric" : column).replaceAll("_", " ")} <span>{sortIndicator}</span>
        </SettingsMenuItem>
    )
}
SortColumnMenuItem.propTypes = {
    column: string,
    disabled: bool,
    sortColumn: stringURLSearchQueryPropType,
    sortDirection: sortDirectionURLSearchQueryPropType,
    handleSort: func,
    help: popupContentPropType,
}
