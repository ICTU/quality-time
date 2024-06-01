import { func } from "prop-types"
import { useContext } from "react"

import { add_subject, copy_subject, move_subject } from "../api/subject"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { Segment } from "../semantic_ui_react_wrappers"
import { reportPropType, reportsPropType, settingsPropType } from "../sharedPropTypes"
import { AddDropdownButton, CopyButton, MoveButton } from "../widgets/Button"
import { subject_options } from "../widgets/menu_options"
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
                <Segment basic>
                    <AddDropdownButton
                        itemType="subject"
                        itemSubtypes={subjectTypes(dataModel.subjects)}
                        onClick={(subtype) => {
                            stopFiltering()
                            add_subject(report.report_uuid, subtype, reload)
                        }}
                    />
                    <CopyButton
                        itemType="subject"
                        onChange={(source_subject_uuid) => {
                            stopFiltering()
                            copy_subject(source_subject_uuid, report.report_uuid, reload)
                        }}
                        get_options={() => subject_options(reports, dataModel)}
                    />
                    <MoveButton
                        itemType="subject"
                        onChange={(source_subject_uuid) => {
                            stopFiltering()
                            move_subject(source_subject_uuid, report.report_uuid, reload)
                        }}
                        get_options={() => subject_options(reports, dataModel, report.report_uuid)}
                    />
                </Segment>
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
