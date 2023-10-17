import React from 'react';
import PropTypes from 'prop-types';
import {
    datePropType,
    datesPropType,
    issueSettingsPropType,
    metricsToHidePropType,
    sortDirectionPropType,
    stringsPropType
} from '../sharedPropTypes';
import { useDelayedRender } from '../utils';
import { Subject } from './Subject';

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
    reports,
    reportsToShow,
    report_date,
    sortColumn,
    sortDirection,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {
    const visible = useDelayedRender();
    const subjects = []
    reportsToShow.forEach((report) => {
        Object.keys(report.subjects).forEach((subject_uuid) => {
            subjects.push([report, subject_uuid])
        })
    })
    const lastIndex = subjects.length - 1;
    return (
        <>
            {subjects.map(([report, subject_uuid], index) =>
                visible || index < 3 ?
                    <Subject
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
                    /> : null
            )}
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
    reports: PropTypes.array,
    reportsToShow: PropTypes.arrayOf(PropTypes.object),
    report_date: datePropType,
    sortColumn: PropTypes.string,
    sortDirection: sortDirectionPropType,
    toggleVisibleDetailsTab: PropTypes.func,
    visibleDetailsTabs: stringsPropType,
}
