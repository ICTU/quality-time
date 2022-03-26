import React from 'react';
import { Container } from 'semantic-ui-react';
import { Segment } from './semantic_ui_react_wrappers';
import { Report } from './report/Report';
import { ReportsOverview } from './report/ReportsOverview';

function getColumnDates(reportDate, dateInterval, dateOrder, nrDates) {
    const baseDate = reportDate ? new Date(reportDate) : new Date();
    const intervalLength = dateInterval;  // dateInterval is in days
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
    hideMetricsNotRequiringAction,
    history,
    loading,
    go_home,
    nrDates,
    nr_measurements,
    open_report,
    reload,
    report_date,
    report_uuid,
    reports,
    reports_overview,
    showIssueCreationDate,
    showIssueSummary,
    showIssueUpdateDate,
    sortColumn,
    sortDirection,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {
    let content;
    if (loading) {
        content = <Segment basic placeholder loading size="massive" aria-label="Loading..." />
    } else {
        const dates = getColumnDates(report_date, dateInterval, dateOrder, nrDates)
        if (report_uuid) {
            content = <Report
                changed_fields={changed_fields}
                dates={dates}
                go_home={go_home}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                history={history}
                nr_measurements={nr_measurements}
                reload={reload}
                report={current_report}
                reports={reports}
                report_date={report_date}
                showIssueCreationDate={showIssueCreationDate}
                showIssueSummary={showIssueSummary}
                showIssueUpdateDate={showIssueUpdateDate}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={visibleDetailsTabs}
            />
        } else {
            content = <ReportsOverview
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
