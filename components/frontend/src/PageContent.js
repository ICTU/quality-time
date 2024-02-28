import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Container, Loader } from 'semantic-ui-react';
import { Segment } from './semantic_ui_react_wrappers';
import { Report } from './report/Report';
import { ReportsOverview } from './report/ReportsOverview';
import { get_measurements } from './api/measurement';
import {
    reportPropType,
    reportsOverviewPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
    optionalDatePropType,
} from './sharedPropTypes';

function getColumnDates(reportDate, dateInterval, dateOrder, nrDates) {
    const baseDate = reportDate ? new Date(reportDate) : new Date();
    const intervalLength = dateInterval ?? 1;  // dateInterval is in days
    nrDates = nrDates ?? 1;
    const columnDates = []
    for (let offset = 0; offset < nrDates * intervalLength; offset += intervalLength) {
        let date = new Date(baseDate);
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
    loading,
    nrMeasurements,
    openReport,
    openReportsOverview,
    reload,
    report_date,
    report_uuid,
    reports,
    reports_overview,
    settings
}) {
    const dates = getColumnDates(report_date, settings.dateInterval.value, settings.dateOrder.value, settings.nrDates.value)
    const [measurements, setMeasurements] = useState([]);
    useEffect(() => {
        const maxDate = report_date ? new Date(report_date) : new Date();
        const minDate = dates.slice().sort((d1, d2) => { return d1.getTime() - d2.getTime() }).at(0);
        minDate.setHours(minDate.getHours() - 1)  // Get at least one hour of measurements
        get_measurements(minDate, maxDate).then(json => {
            setMeasurements(json.measurements ?? [])
        })
        // eslint-disable-next-line
    }, [report_date, nrMeasurements, settings.dateInterval.value, settings.nrDates.value]);
    let content;
    if (loading) {
        content = <Segment basic placeholder aria-label="Loading..."><Loader active size="massive" /></Segment>
    } else {
        const commonProps = {
            changed_fields: changed_fields,
            dates: dates,
            handleSort: handleSort,
            measurements: measurements,
            reload: reload,
            reports: reports,
            report_date: report_date,
            settings: settings
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
    handleSort: PropTypes.func,
    loading: PropTypes.bool,
    nrMeasurements: PropTypes.number,
    openReport: PropTypes.func,
    openReportsOverview: PropTypes.func,
    reload: PropTypes.func,
    report_date: optionalDatePropType,
    report_uuid: PropTypes.string,
    reports: reportsPropType,
    reports_overview: reportsOverviewPropType,
    settings: settingsPropType
}
