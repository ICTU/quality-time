import { useContext } from 'react';
import PropTypes from 'prop-types';
import { Segment } from '../semantic_ui_react_wrappers';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { AddDropdownButton, CopyButton, MoveButton } from '../widgets/Button';
import { add_subject, copy_subject, move_subject } from '../api/subject';
import { subject_options } from '../widgets/menu_options';
import { subjectTypes } from './SubjectType';
import { reportPropType, reportsPropType, settingsPropType } from '../sharedPropTypes';

export function SubjectsButtonRow({ reload, report, reports, settings }) {
    const dataModel = useContext(DataModel)
    function stopFiltering() {
        settings.metricsToHide.reset()
        settings.hiddenTags.reset()
    }
    return (
        <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
            <Segment basic>
                <AddDropdownButton
                    item_type="subject"
                    item_subtypes={subjectTypes(dataModel)}
                    onClick={(subtype) => { stopFiltering(); add_subject(report.report_uuid, subtype, reload) }}
                />
                <CopyButton
                    item_type="subject"
                    onChange={(source_subject_uuid) => { stopFiltering(); copy_subject(source_subject_uuid, report.report_uuid, reload) }}
                    get_options={() => subject_options(reports, dataModel)}
                />
                <MoveButton
                    item_type="subject"
                    onChange={(source_subject_uuid) => { stopFiltering(); move_subject(source_subject_uuid, report.report_uuid, reload) }}
                    get_options={() => subject_options(reports, dataModel, report.report_uuid)}
                />
            </Segment>}
        />
    )
}
SubjectsButtonRow.propTypes = {
    reload: PropTypes.func,
    report: reportPropType,
    reports: reportsPropType,
    settings: settingsPropType
}
