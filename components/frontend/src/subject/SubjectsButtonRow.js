import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { Segment } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { AddDropdownButton, CopyButton, MoveButton } from '../widgets/Button';
import { add_subject, copy_subject, move_subject } from '../api/subject';
import { subject_options } from '../widgets/menu_options';
import { subjectTypes } from './SubjectType';

export function SubjectsButtonRow({ reload, report, reports }) {
    const dataModel = useContext(DataModel)
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <Segment basic>
                <AddDropdownButton
                    item_type="subject"
                    item_subtypes={subjectTypes(dataModel)}
                    onClick={(subtype) => { add_subject(report.report_uuid, subtype, reload) }}
                />
                <CopyButton
                    item_type="subject"
                    onChange={(source_subject_uuid) => copy_subject(source_subject_uuid, report.report_uuid, reload)}
                    get_options={() => subject_options(reports, dataModel)}
                />
                <MoveButton
                    item_type="subject"
                    onChange={(source_subject_uuid) => move_subject(source_subject_uuid, report.report_uuid, reload)}
                    get_options={() => subject_options(reports, dataModel, report.report_uuid)}
                />
            </Segment>}
        />
    )
}
SubjectsButtonRow.propTypes = {
    reload: PropTypes.func,
    report: PropTypes.object,
    reports: PropTypes.array
}