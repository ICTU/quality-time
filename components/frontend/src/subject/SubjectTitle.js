import { bool, func, object, string } from "prop-types"
import { useContext } from "react"
import { Icon, Menu } from "semantic-ui-react"

import { delete_subject, set_subject_attribute } from "../api/subject"
import { activeTabIndex, tabChangeHandler } from "../app_ui_settings"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { Header, Tab } from "../semantic_ui_react_wrappers"
import { reportPropType, settingsPropType } from "../sharedPropTypes"
import { getSubjectType, slugify } from "../utils"
import { DeleteButton, PermLinkButton, ReorderButtonGroup } from "../widgets/Button"
import { FocusableTab } from "../widgets/FocusableTab"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { HyperLink } from "../widgets/HyperLink"
import { SubjectParameters } from "./SubjectParameters"

function SubjectHeader({ subjectType }) {
    const url = `https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/reference.html${slugify(subjectType.name)}`
    return (
        <Header>
            <Header.Content>
                {subjectType.name}
                <Header.Subheader>
                    {subjectType.description}{" "}
                    <HyperLink url={url}>
                        Read the Docs <Icon name="external" link />
                    </HyperLink>
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}
SubjectHeader.propTypes = {
    subjectType: object,
}

function ButtonRow({ subject_uuid, firstSubject, lastSubject, reload, url }) {
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <>
                    <ReorderButtonGroup
                        first={firstSubject}
                        last={lastSubject}
                        moveable="subject"
                        onClick={(direction) => {
                            set_subject_attribute(subject_uuid, "position", direction, reload)
                        }}
                    />
                    <PermLinkButton itemType="subject" url={url} />
                    <DeleteButton itemType="subject" onClick={() => delete_subject(subject_uuid, reload)} />
                </>
            }
        />
    )
}
ButtonRow.propTypes = {
    subject_uuid: string,
    firstSubject: bool,
    lastSubject: bool,
    reload: func,
    url: string,
}

export function SubjectTitle({
    atReportsOverview,
    report,
    subject,
    subject_uuid,
    firstSubject,
    lastSubject,
    reload,
    settings,
}) {
    const dataModel = useContext(DataModel)
    const tabIndex = activeTabIndex(settings.expandedItems, subject_uuid)
    const subjectType = getSubjectType(subject.type, dataModel.subjects) || { name: "Unknown subject type" }
    const subjectName = subject.name || subjectType.name
    const subjectTitle = (atReportsOverview ? report.title + " ❯ " : "") + subjectName
    const subjectUrl = `${window.location}#${subject_uuid}`
    const panes = [
        {
            menuItem: (
                <Menu.Item key="configuration">
                    <Icon name="settings" />
                    <FocusableTab>{"Configuration"}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <SubjectParameters
                        subject={subject}
                        subject_uuid={subject_uuid}
                        subject_name={subjectName}
                        reload={reload}
                    />
                </Tab.Pane>
            ),
        },
        {
            menuItem: (
                <Menu.Item key="changelog">
                    <Icon name="history" />
                    <FocusableTab>{"Changelog"}</FocusableTab>
                </Menu.Item>
            ),
            render: () => (
                <Tab.Pane>
                    <ChangeLog subject_uuid={subject_uuid} timestamp={report.timestamp} />
                </Tab.Pane>
            ),
        },
    ]

    return (
        <HeaderWithDetails
            className="sticky"
            header={subjectTitle}
            item_uuid={`${subject_uuid}:${tabIndex}`}
            level="h2"
            settings={settings}
            style={{ marginTop: 50 }}
            subheader={subject.subtitle}
        >
            <SubjectHeader subjectType={subjectType} />
            <Tab
                defaultActiveIndex={tabIndex}
                onTabChange={tabChangeHandler(settings.expandedItems, subject_uuid)}
                panes={panes}
            />
            <div style={{ marginTop: "20px" }}>
                <ButtonRow
                    subject_uuid={subject_uuid}
                    firstSubject={firstSubject}
                    lastSubject={lastSubject}
                    reload={reload}
                    url={subjectUrl}
                />
            </div>
        </HeaderWithDetails>
    )
}
SubjectTitle.propTypes = {
    atReportsOverview: bool,
    firstSubject: bool,
    lastSubject: bool,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    subject: object,
    subject_uuid: string,
}
