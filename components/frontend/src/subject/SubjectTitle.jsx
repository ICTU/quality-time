import "./SubjectTitle.css"

import HistoryIcon from "@mui/icons-material/History"
import SettingsIcon from "@mui/icons-material/Settings"
import { bool, func, object, string } from "prop-types"
import { useContext } from "react"

import { deleteSubject, setSubjectAttribute } from "../api/subject"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { zIndexSubjectTitle } from "../defaults"
import { reportPropType, settingsPropType } from "../sharedPropTypes"
import { getSubjectType } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { PermLinkButton } from "../widgets/buttons/PermLinkButton"
import { ReorderButtonGroup } from "../widgets/buttons/ReorderButtonGroup"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { Tabs } from "../widgets/Tabs"
import { SubjectParameters } from "./SubjectParameters"

function SubjectTitleButtonRow({ firstSubject, lastSubject, reload, settings, subjectUuid, url }) {
    const deleteButton = (
        <DeleteButton
            itemType="subject"
            onClick={() => {
                deleteSubject(subjectUuid, reload)
                settings.expandedItems.deleteItem(subjectUuid)
            }}
        />
    )
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow rightButton={deleteButton} paddingBottom={2} paddingLeft={0} paddingRight={0} paddingTop={2}>
                    <ReorderButtonGroup
                        first={firstSubject}
                        last={lastSubject}
                        moveable="subject"
                        onClick={(direction) => {
                            setSubjectAttribute(subjectUuid, "position", direction, reload)
                        }}
                    />
                    <PermLinkButton itemType="subject" url={url} />
                </ButtonRow>
            }
        />
    )
}
SubjectTitleButtonRow.propTypes = {
    firstSubject: bool,
    lastSubject: bool,
    reload: func,
    settings: settingsPropType,
    subjectUuid: string,
    url: string,
}

export function SubjectTitle({
    atReportsOverview,
    report,
    subject,
    subjectUuid,
    firstSubject,
    lastSubject,
    reload,
    settings,
}) {
    const dataModel = useContext(DataModel)
    const subjectType = getSubjectType(subject.type, dataModel.subjects)
    const subjectName = subject.name || subjectType.name
    const subjectTitle = (atReportsOverview ? report.title + " ❯ " : "") + subjectName
    const subjectUrl = `${globalThis.location}#${subjectUuid}`
    return (
        <div className="sticky" style={{ zIndex: zIndexSubjectTitle }}>
            <HeaderWithDetails
                header={subjectTitle}
                itemUuid={subjectUuid}
                level="h2"
                settings={settings}
                subheader={subject.subtitle}
            >
                <Tabs
                    settings={settings}
                    tabs={[
                        { label: "Configuration", icon: <SettingsIcon /> },
                        { label: "Changelog", icon: <HistoryIcon /> },
                    ]}
                    uuid={subjectUuid}
                >
                    <SubjectParameters
                        subject={subject}
                        subjectUuid={subjectUuid}
                        subjectName={subjectName}
                        reload={reload}
                    />
                    <ChangeLog subjectUuid={subjectUuid} timestamp={report.timestamp} />
                </Tabs>
                <SubjectTitleButtonRow
                    subjectUuid={subjectUuid}
                    firstSubject={firstSubject}
                    lastSubject={lastSubject}
                    reload={reload}
                    settings={settings}
                    url={subjectUrl}
                />
            </HeaderWithDetails>
        </div>
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
    subjectUuid: string,
}
