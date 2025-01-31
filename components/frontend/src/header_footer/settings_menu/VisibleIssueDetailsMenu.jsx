import { string } from "prop-types"

import { boolURLSearchQueryPropType, popupContentPropType, settingsPropType } from "../../sharedPropTypes"
import { SettingsMenu, SettingsMenuItem } from "./SettingsMenu"

export function VisibleIssueDetailsMenu({ settings }) {
    return (
        <SettingsMenu title="Visible issue details">
            <IssueAttributeMenuItem
                issueAttributeName="Summary"
                issueAttribute={settings.showIssueSummary}
                help="Next to the issue status, also show the issue summary. Note: the popup over the issue always shows the issue summary, regardless of this setting."
            />
            <IssueAttributeMenuItem
                issueAttributeName="Creation date"
                issueAttribute={settings.showIssueCreationDate}
                help="Next to the issue status, also show how long ago issue were created. Note: the popup over the issue always shows the exact date when the issue was created, regardless of this setting."
            />
            <IssueAttributeMenuItem
                issueAttributeName="Update date"
                issueAttribute={settings.showIssueUpdateDate}
                help="Next to the issue status, also show how long ago issues were last updated. Note: the popup over the issue always shows the exact date when the issue was last updated, regardless of this setting."
            />
            <IssueAttributeMenuItem
                issueAttributeName="Due date"
                issueAttribute={settings.showIssueDueDate}
                help="Next to the issue status, also show the due date of issues. Note: the popup over the issue always shows the due date, if the issue has one, regardless of this setting."
            />
            <IssueAttributeMenuItem
                issueAttributeName="Release"
                issueAttribute={settings.showIssueRelease}
                help="Next to the issue status, also show the release issues are assigned to. Note: the popup over the issue always shows the release, if the issue has one, regardless of this setting."
            />
            <IssueAttributeMenuItem
                issueAttributeName="Sprint"
                issueAttribute={settings.showIssueSprint}
                help="Next to the issue status, also show the sprint issues are assigned to. Note: the popup over the issue always shows the sprint, if the issue has one, regardless of this setting."
            />
        </SettingsMenu>
    )
}
VisibleIssueDetailsMenu.propTypes = {
    settings: settingsPropType,
}

function IssueAttributeMenuItem({ help, issueAttributeName, issueAttribute }) {
    return (
        <SettingsMenuItem
            active={issueAttribute.value}
            help={help}
            onClick={issueAttribute.set}
            onClickData={!issueAttribute.value}
        >
            {issueAttributeName}
        </SettingsMenuItem>
    )
}
IssueAttributeMenuItem.propTypes = {
    help: popupContentPropType,
    issueAttributeName: string,
    issueAttribute: boolURLSearchQueryPropType,
}
