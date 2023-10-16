import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Container, Loader } from 'semantic-ui-react';
import { Segment } from './semantic_ui_react_wrappers';
import { Report } from './report/Report';
import { ReportsOverview } from './report/ReportsOverview';
import { get_measurements } from './api/measurement';
import { metricsToHidePropType } from './sharedPropTypes';

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
    metricsToHide,
    issueSettings,
    loading,
    nrDates,
    nrMeasurements,
    open_report,
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
        if (report_uuid) {
            content = <Report
                changed_fields={changed_fields}
                dates={dates}
                openReportsOverview={openReportsOverview}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                hiddenTags={hiddenTags}
                metricsToHide={metricsToHide}
                issueSettings={issueSettings}
                measurements={measurements}
                reload={reload}
                report={current_report}
                reports={reports}
                report_date={report_date}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                toggleHiddenTag={toggleHiddenTag}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={visibleDetailsTabs}
            />
        } else {
            content = <ReportsOverview
                dates={dates}
                hiddenTags={hiddenTags}
                measurements={measurements}
                open_report={open_report}
                reload={reload}
                reports={reports}
                reports_overview={reports_overview}
                report_date={report_date}
            />
        }
    }
    return <Container fluid className="MainContainer">{content}</Container>
}
PageContent.propTypes = {
    hiddenTags: PropTypes.arrayOf(PropTypes.string),
    metricsToHide: metricsToHidePropType,
    openReportsOverview: PropTypes.func,
    toggleHiddenTag: PropTypes.func
}
