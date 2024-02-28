import PropTypes from 'prop-types';
import { Table } from '../semantic_ui_react_wrappers';
import { SubjectTableRow } from './SubjectTableRow';
import {
    datesPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from '../sharedPropTypes';

export function SubjectTableBody(
    {
        changed_fields,
        dates,
        handleSort,
        measurements,
        metricEntries,
        reload,
        report,
        reportDate,
        reports,
        reversedMeasurements,
        settings,
        subject_uuid
    }
) {
    const lastIndex = metricEntries.length - 1;
    return (
        <Table.Body>
            {metricEntries.map(([metric_uuid, metric], index) => {
                return (
                    <SubjectTableRow
                        changed_fields={changed_fields}
                        dates={dates}
                        handleSort={handleSort}
                        index={index}
                        key={metric_uuid}
                        lastIndex={lastIndex}
                        measurements={measurements}
                        metric_uuid={metric_uuid}
                        metric={metric}
                        reload={reload}
                        report={report}
                        reportDate={reportDate}
                        reports={reports}
                        reversedMeasurements={reversedMeasurements}
                        settings={settings}
                        subject_uuid={subject_uuid}
                    />
                )
            })}
        </Table.Body>
    )
}
SubjectTableBody.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: PropTypes.func,
    measurements: PropTypes.array,
    metricEntries: PropTypes.array,
    reload: PropTypes.func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    reversedMeasurements: PropTypes.array,
    settings: settingsPropType,
    subject_uuid: PropTypes.string,
}
