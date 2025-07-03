import { bool, func } from "prop-types"

import { settingsPropType, stringsPropType } from "../sharedPropTypes"
import { SettingsMenuGroup } from "./settings_menu/SettingsMenu"
import { SortColumnMenu } from "./settings_menu/SortColumnMenu"
import { VisibleCardMenu } from "./settings_menu/VisibleCardMenu"
import { VisibleColumnMenu } from "./settings_menu/VisibleColumnsMenu"
import { VisibleIssueDetailsMenu } from "./settings_menu/VisibleIssueDetailsMenu"
import { VisibleMetricMenu } from "./settings_menu/VisibleMetricMenu"
import { VisibleTagMenu } from "./settings_menu/VisibleTagMenu"

export function SettingsPanel({ atReportsOverview, handleSort, settings, tags }) {
    return (
        <SettingsMenuGroup>
            <VisibleCardMenu atReportsOverview={atReportsOverview} settings={settings} />
            <VisibleMetricMenu settings={settings} />
            <VisibleTagMenu tags={tags} settings={settings} />
            <VisibleColumnMenu settings={settings} />
            <SortColumnMenu handleSort={handleSort} settings={settings} />
            <VisibleIssueDetailsMenu settings={settings} />
        </SettingsMenuGroup>
    )
}
SettingsPanel.propTypes = {
    atReportsOverview: bool,
    handleSort: func,
    tags: stringsPropType.isRequired,
    settings: settingsPropType,
}
