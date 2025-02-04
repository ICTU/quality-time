import HistoryIcon from "@mui/icons-material/History"
import SettingsIcon from "@mui/icons-material/Settings"
import { bool, func, object, string } from "prop-types"
import { useContext } from "react"

import { delete_subject, set_subject_attribute } from "../api/subject"
import { ChangeLog } from "../changelog/ChangeLog"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { reportPropType, settingsPropType } from "../sharedPropTypes"
import { getSubjectType } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { PermLinkButton } from "../widgets/buttons/PermLinkButton"
import { ReorderButtonGroup } from "../widgets/buttons/ReorderButtonGroup"
import { HeaderWithDetails } from "../widgets/HeaderWithDetails"
import { Tabs } from "../widgets/Tabs"
import { SubjectParameters } from "./SubjectParameters"

function SubjectTitleButtonRow({ subject_uuid, firstSubject, lastSubject, reload, url }) {
    const deleteButton = <DeleteButton itemType="subject" onClick={() => delete_subject(subject_uuid, reload)} />
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
                            set_subject_attribute(subject_uuid, "position", direction, reload)
                        }}
                    />
                    <PermLinkButton itemType="subject" url={url} />
                </ButtonRow>
            }
        />
    )
}
SubjectTitleButtonRow.propTypes = {
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
    const subjectType = getSubjectType(subject.type, dataModel.subjects)
    const subjectName = subject.name || subjectType.name
    const subjectTitle = (atReportsOverview ? report.title + " ❯ " : "") + subjectName
    const subjectUrl = `${window.location}#${subject_uuid}`
    return (
        <HeaderWithDetails
            header={subjectTitle}
            item_uuid={subject_uuid}
            level="h2"
            settings={settings}
            subheader={subject.subtitle}
        >
            <Tabs
                tabs={[
                    { label: "Configuration", icon: <SettingsIcon /> },
                    { label: "Changelog", icon: <HistoryIcon /> },
                ]}
            >
                <SubjectParameters
                    subject={subject}
                    subject_uuid={subject_uuid}
                    subject_name={subjectName}
                    reload={reload}
                />
                <ChangeLog subject_uuid={subject_uuid} timestamp={report.timestamp} />
            </Tabs>
            <SubjectTitleButtonRow
                subject_uuid={subject_uuid}
                firstSubject={firstSubject}
                lastSubject={lastSubject}
                reload={reload}
                url={subjectUrl}
            />
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
