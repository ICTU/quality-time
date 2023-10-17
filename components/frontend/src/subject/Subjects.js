import React from 'react';
import PropTypes from 'prop-types';
import {
    datePropType,
    datesPropType,
    issueSettingsPropType,
    metricsToHidePropType,
    reportsPropType,
    sortDirectionPropType,
    stringsPropType
} from '../sharedPropTypes';
import { useDelayedRender } from '../utils';
import { Subject } from './Subject';

export function Subjects({
    atReportsOverview,
    changed_fields,
    dates,
    handleSort,
    hiddenColumns,
    hiddenTags,
    issueSettings,
    measurements,
    metricsToHide,
    reload,
    reports,
    reportsToShow,
    report_date,
    sortColumn,
    sortDirection,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {
    // Assume max 3 subjects are visible below the dashboard when the page is initially rendered
    const nrSubjectsVisibleOnInitialRender = 3
    const visible = useDelayedRender();
    const subjects = []
    reportsToShow.forEach((report) => {
        const lastIndex = Object.keys(report.subjects).length - 1;
        Object.keys(report.subjects).forEach((subject_uuid, index) => {
            if (!visible && subjects.length > nrSubjectsVisibleOnInitialRender) { return }
            subjects.push(
                <Subject
                    atReportsOverview={atReportsOverview}
                    changed_fields={changed_fields}
                    dates={dates}
                    firstSubject={index === 0}
                    handleSort={handleSort}
                    hiddenColumns={hiddenColumns}
                    hiddenTags={hiddenTags}
                    issueSettings={issueSettings}
                    key={subject_uuid}
                    lastSubject={index === lastIndex}
                    measurements={measurements}
                    metricsToHide={metricsToHide}
                    reload={reload}
                    report={report}
                    reports={reports}
                    report_date={report_date}
                    sortColumn={sortColumn}
                    sortDirection={sortDirection}
                    subject_uuid={subject_uuid}
                    toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                    visibleDetailsTabs={visibleDetailsTabs}
                />
            )
        })
    })
    return subjects
}
Subjects.propTypes = {
    atReportsOverview: PropTypes.bool,
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: PropTypes.func,
    hiddenColumns: stringsPropType,
    hiddenTags: stringsPropType,
    issueSettings: issueSettingsPropType,
    measurements: PropTypes.array,
    metricsToHide: metricsToHidePropType,
    reload: PropTypes.func,
    reports: reportsPropType,
    reportsToShow: reportsPropType,
    report_date: datePropType,
    sortColumn: PropTypes.string,
    sortDirection: sortDirectionPropType,
    toggleVisibleDetailsTab: PropTypes.func,
    visibleDetailsTabs: stringsPropType,
}
