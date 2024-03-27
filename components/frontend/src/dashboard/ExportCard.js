import { Card, List } from 'semantic-ui-react';
import { childrenPropType, datePropType, reportPropType } from '../sharedPropTypes';
import { bool, string } from 'prop-types';
import './ExportCard.css';

function ExportCardItem({ children, url }) {
    const item = children;
    return url ? <List.Item as="a" href={url}>{item}</List.Item> : <List.Item>{item}</List.Item>;
}
ExportCardItem.propTypes = {
    children: childrenPropType,
    url: string,
}

export function ExportCard({ lastUpdate, report, reportDate, isOverview = false }) {
    const reportURL = new URLSearchParams(window.location.search).get("report_url") ?? window.location.href;
    const title = isOverview ? "About these reports" : "About this report";
    const listItems = [
        <List.Item key={"reportURL"} data-testid={"reportUrl"}>
            <List.Content verticalAlign={"middle"}>
                <ExportCardItem url={reportURL}>{report.title}</ExportCardItem>
            </List.Content>
        </List.Item>,
        <List.Item key={"date"}>
            <List.Content verticalAlign={"middle"}>
                <ExportCardItem>{"Report date: " + formatDate(reportDate ?? new Date())}</ExportCardItem>
            </List.Content>
        </List.Item>,
        <List.Item key={"generated"}>
            <List.Content verticalAlign={"middle"}>
                <ExportCardItem>{"Generated: " + formatDate(lastUpdate) + ", " + formatTime(lastUpdate)}</ExportCardItem>
            </List.Content>
        </List.Item>,
        <List.Item key={"version"} data-testid={"version"}>
            <List.Content verticalAlign={"middle"} >
                <ExportCardItem url={`https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/changelog.html`}><em>Quality-time</em> v{process.env.REACT_APP_VERSION}</ExportCardItem>
            </List.Content>
        </List.Item>
    ];
    return (
        <Card tabIndex="0" className="export-data-card">
            <Card.Content>
                <Card.Header title={title} textAlign='center'>{title}</Card.Header>
                <List size="small">
                    {listItems}
                </List>
            </Card.Content>
        </Card>
    )
}
ExportCard.propTypes = {
    isOverview: bool,
    lastUpdate: datePropType,
    report: reportPropType,
    reportDate: datePropType,
}

// Hard code en-GB to get European style dates and times. See https://github.com/ICTU/quality-time/issues/8381.

function formatDate(date) {
    return date.toLocaleDateString('en-GB', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '-');
}

function formatTime(date) {
    return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
}
