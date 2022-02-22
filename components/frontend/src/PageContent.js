import React from 'react';
import { Container } from 'semantic-ui-react';
import { Segment } from './semantic_ui_react_wrappers/Segment';
import { Report } from './report/Report';
import { ReportsOverview } from './report/ReportsOverview';

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
    sortColumn,
    sortDirection,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {
    let content;
    if (loading) {
        content = <Segment basic placeholder loading size="massive" aria-label="Loading..." />
    } else if (report_uuid) {
        content = <Report
            changed_fields={changed_fields}
            dateInterval={dateInterval}
            dateOrder={dateOrder}
            go_home={go_home}
            handleSort={handleSort}
            hiddenColumns={hiddenColumns}
            hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
            history={history}
            nrDates={nrDates}
            nr_measurements={nr_measurements}
            reload={reload}
            report={current_report}
            reports={reports}
            report_date={report_date}
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
    return <Container fluid className="MainContainer">{content}</Container>
}
