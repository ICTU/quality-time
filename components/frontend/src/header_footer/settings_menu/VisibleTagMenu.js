import { string } from "prop-types"

import { settingsPropType, stringsPropType, stringsURLSearchQueryPropType } from "../../sharedPropTypes"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function VisibleTagMenu({ settings, tags }) {
    return (
        <SettingsMenu title="Visible tags">
            {tags.map((tag) => (
                <VisibleTagMenuItem key={tag} tag={tag} hiddenTags={settings.hiddenTags} />
            ))}
        </SettingsMenu>
    )
}
VisibleTagMenu.propTypes = {
    settings: settingsPropType,
    tags: stringsPropType.isRequired,
}

function VisibleTagMenuItem({ tag, hiddenTags }) {
    return (
        <SettingsMenuItem active={hiddenTags.excludes(tag)} onClick={hiddenTags.toggle} onClickData={tag}>
            {tag}
        </SettingsMenuItem>
    )
}
VisibleTagMenuItem.propTypes = {
    tag: string,
    hiddenTags: stringsURLSearchQueryPropType,
}
