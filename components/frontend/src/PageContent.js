import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Container, Loader } from 'semantic-ui-react';
import { Segment } from './semantic_ui_react_wrappers';
import { Report } from './report/Report';
import { ReportsOverview } from './report/ReportsOverview';
import { get_measurements } from './api/measurement';
import {
    datePropType,
    issueSettingsPropType,
    metricsToHidePropType,
    reportPropType,
    reportsPropType,
    sortDirectionPropType,
    stringsPropType
} from './sharedPropTypes';

function getColumnDates(reportDate, dateInterval, dateOrder, nrDates) {
    const baseDate = reportDate ? new Date(reportDate) : new Date();
    const intervalLength = dateInterval ?? 1;  // dateInterval is in days
    nrDates = nrDates ?? 1;
    const columnDates = []
    for (let offset = 0; offset < nrDates * intervalLength; offset += intervalLength) {
        let date = new Date(baseDate.getTime());
        date.setDate(date.getDate() - offset);
        columnDates.push(date)
    }
    if (dateOrder === "ascending") { columnDates.reverse() }
    return columnDates
}

export function PageContent({
    changed_fields,
    current_report,
    dateInterval,
    dateOrder,
    handleSort,
    hiddenColumns,
    hiddenTags,
    issueSettings,
    metricsToHide,
    loading,
    nrDates,
    nrMeasurements,
    openReport,
    openReportsOverview,
    reload,
    report_date,
    report_uuid,
    reports,
    reports_overview,
    sortColumn,
    sortDirection,
    toggleHiddenTag,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {
    const dates = getColumnDates(report_date, dateInterval, dateOrder, nrDates)
    const [measurements, setMeasurements] = useState([]);
    useEffect(() => {
        const minReportDate = dates.slice().sort((d1, d2) => { return d1.getTime() - d2.getTime() }).at(0);
        get_measurements(report_date, minReportDate).then(json => {
            setMeasurements(json.measurements ?? [])
        })
        // eslint-disable-next-line
    }, [report_date, nrMeasurements, dateInterval, nrDates]);
    let content;
    if (loading) {
        content = <Segment basic placeholder aria-label="Loading..."><Loader active size="massive" /></Segment>
    } else {
        const commonProps = {
            changed_fields: changed_fields,
            dates: dates,
            handleSort: handleSort,
            hiddenColumns: hiddenColumns,
            hiddenTags: hiddenTags,
            issueSettings: issueSettings,
            measurements: measurements,
            metricsToHide: metricsToHide,
            reload: reload,
            reports: reports,
            report_date: report_date,
            sortColumn: sortColumn,
            sortDirection: sortDirection,
            toggleHiddenTag: toggleHiddenTag,
            toggleVisibleDetailsTab: toggleVisibleDetailsTab,
            visibleDetailsTabs: visibleDetailsTabs
        }
        if (report_uuid) {
            content = <Report
                openReportsOverview={openReportsOverview}
                report={current_report}
                {...commonProps}
            />
        } else {
            content = <ReportsOverview
                openReport={openReport}
                reports_overview={reports_overview}
                {...commonProps}
            />
        }
    }
    return <Container fluid className="MainContainer">{content}</Container>
}
PageContent.propTypes = {
    changed_fields: stringsPropType,
    current_report: reportPropType,
    dateInterval: PropTypes.number,
    dateOrder: sortDirectionPropType,
    handleSort: PropTypes.func,
    hiddenColumns: stringsPropType,
    hiddenTags: stringsPropType,
    issueSettings: issueSettingsPropType,
    metricsToHide: metricsToHidePropType,
    loading: PropTypes.bool,
    nrDates: PropTypes.number,
    nrMeasurements: PropTypes.number,
    openReport: PropTypes.func,
    openReportsOverview: PropTypes.func,
    reload: PropTypes.func,
    report_date: datePropType,
    report_uuid: PropTypes.string,
    reports: reportsPropType,
    reports_overview: PropTypes.object,
    sortColumn: PropTypes.string,
    sortDirection: sortDirectionPropType,
    toggleHiddenTag: PropTypes.func,
    toggleVisibleDetailsTab: PropTypes.func,
    visibleDetailsTabs: stringsPropType
}
