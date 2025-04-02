import { func } from "prop-types"
import { useContext } from "react"

import { addSubject, copySubject, moveSubject } from "../api/subject"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { reportPropType, reportsPropType, settingsPropType } from "../sharedPropTypes"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddDropdownButton } from "../widgets/buttons/AddDropdownButton"
import { CopyButton } from "../widgets/buttons/CopyButton"
import { MoveButton } from "../widgets/buttons/MoveButton"
import { subjectOptions } from "../widgets/menu_options"
import { subjectTypes } from "./SubjectType"

export function SubjectsButtonRow({ reload, report, reports, settings }) {
    const dataModel = useContext(DataModel)
    function stopFiltering() {
        settings.metricsToHide.reset()
        settings.hiddenTags.reset()
    }
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow paddingLeft={0} paddingTop={7}>
                    <AddDropdownButton
                        itemType="subject"
                        itemSubtypes={subjectTypes(dataModel.subjects)}
                        onClick={(subtype) => {
                            stopFiltering()
                            addSubject(report.report_uuid, subtype, reload)
                        }}
                        sort={false} // Don't sort the subjects by name because it's a hierarchy defined in the data model
                    />
                    <CopyButton
                        itemType="subject"
                        onChange={(subjectUuid) => {
                            stopFiltering()
                            copySubject(subjectUuid, report.report_uuid, reload)
                        }}
                        getOptions={() => subjectOptions(reports, dataModel)}
                    />
                    <MoveButton
                        itemType="subject"
                        onChange={(subjectUuid) => {
                            stopFiltering()
                            moveSubject(subjectUuid, report.report_uuid, reload)
                        }}
                        getOptions={() => subjectOptions(reports, dataModel, report.report_uuid)}
                    />
                </ButtonRow>
            }
        />
    )
}
SubjectsButtonRow.propTypes = {
    reload: func,
    report: reportPropType,
    reports: reportsPropType,
    settings: settingsPropType,
}
