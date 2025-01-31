import { bool } from "prop-types"

import { hiddenCardsPropType, settingsPropType, stringsURLSearchQueryPropType } from "../../sharedPropTypes"
import { capitalize } from "../../utils"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function VisibleCardMenu({ atReportsOverview, settings }) {
    const cardsMenuItemProps = { hiddenCards: settings.hiddenCards }
    return (
        <SettingsMenu title="Visible cards">
            <VisibleCardsMenuItem cards={atReportsOverview ? "reports" : "subjects"} {...cardsMenuItemProps} />
            <VisibleCardsMenuItem cards="tags" {...cardsMenuItemProps} />
            <VisibleCardsMenuItem cards="issues" {...cardsMenuItemProps} />
            <VisibleCardsMenuItem cards="action_required" {...cardsMenuItemProps} />
            <VisibleCardsMenuItem cards="legend" {...cardsMenuItemProps} />
        </SettingsMenu>
    )
}
VisibleCardMenu.propTypes = {
    atReportsOverview: bool,
    settings: settingsPropType,
}

function VisibleCardsMenuItem({ cards, hiddenCards }) {
    return (
        <SettingsMenuItem active={hiddenCards.excludes(cards)} onClick={hiddenCards.toggle} onClickData={cards}>
            {capitalize(cards)}
        </SettingsMenuItem>
    )
}
VisibleCardsMenuItem.propTypes = {
    cards: hiddenCardsPropType,
    hiddenCards: stringsURLSearchQueryPropType,
}
