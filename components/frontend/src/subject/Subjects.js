import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { Segment } from '../semantic_ui_react_wrappers';
import {
    datePropType,
    datesPropType,
    issueSettingsPropType,
    metricsToHidePropType,
    sortDirectionPropType,
    stringsPropType
} from '../sharedPropTypes';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { AddDropdownButton, CopyButton, MoveButton } from '../widgets/Button';
import { add_subject, copy_subject, move_subject } from '../api/subject';
import { subject_options } from '../widgets/menu_options';
import { useDelayedRender } from '../utils';
import { Subject } from './Subject';
import { subjectTypes } from './SubjectType';

export function Subjects({
    changed_fields,
    dates,
    handleSort,
    hiddenColumns,
    hiddenTags,
    metricsToHide,
    issueSettings,
    measurements,
    reload,
    report,
    reports,
    report_date,
    sortColumn,
    sortDirection,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {
    const visible = useDelayedRender();
    const dataModel = useContext(DataModel)
    const lastIndex = Object.keys(report.subjects).length - 1;
    return (
        <>
            {Object.keys(report.subjects).map((subject_uuid, index) =>
                visible || index < 3 ?
                    <Subject
                        changed_fields={changed_fields}
                        dates={dates}
                        firstSubject={index === 0}
                        handleSort={handleSort}
                        hiddenColumns={hiddenColumns}
                        hiddenTags={hiddenTags}
                        metricsToHide={metricsToHide}
                        issueSettings={issueSettings}
                        key={subject_uuid}
                        lastSubject={index === lastIndex}
                        measurements={measurements}
                        report={report}
                        report_date={report_date}
                        reports={reports}
                        sortColumn={sortColumn}
                        sortDirection={sortDirection}
                        subject_uuid={subject_uuid}
                        toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                        visibleDetailsTabs={visibleDetailsTabs}
                        reload={reload}
                    /> : null
            )}
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
        </>
    )
}
Subjects.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: PropTypes.func,
    hiddenColumns: stringsPropType,
    hiddenTags: stringsPropType,
    issueSettings: issueSettingsPropType,
    measurements: PropTypes.array,
    metricsToHide: metricsToHidePropType,
    reload: PropTypes.func,
    report: PropTypes.object,
    reports: PropTypes.array,
    report_date: datePropType,
    sortColumn: PropTypes.string,
    sortDirection: sortDirectionPropType,
    toggleVisibleDetailsTab: PropTypes.func,
    visibleDetailsTabs: stringsPropType,
}
