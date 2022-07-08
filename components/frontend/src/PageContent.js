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
    handleSort,
    history,
    issueSettings,
    loading,
    go_home,
    nr_measurements,
    open_report,
    reload,
    report_date,
    report_uuid,
    reports,
    reports_overview,
    settings,
    toggleVisibleDetailsTab,
}) {
    let content;
    if (loading) {
        content = <Segment basic placeholder loading size="massive" aria-label="Loading..." />
    } else {
        const dates = getColumnDates(report_date, settings.date_interval, settings.date_order, settings.nr_dates)
        if (report_uuid) {
            content = <Report
                changed_fields={changed_fields}
                dates={dates}
                go_home={go_home}
                handleSort={handleSort}
                hiddenColumns={settings.hidden_columns}
                hideMetricsNotRequiringAction={settings.hide_metrics_not_requiring_action}
                history={history}
                nr_measurements={nr_measurements}
                reload={reload}
                report={current_report}
                reports={reports}
                report_date={report_date}
                showIssueCreationDate={settings.show_issue_creation_date}
                showIssueSummary={settings.show_issue_summary}
                showIssueUpdateDate={settings.show_issue_update_date}
                sortColumn={settings.sort_column}
                sortDirection={settings.sort_direction}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={settings.tabs}
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
