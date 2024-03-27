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

export function ExportCard({ report, last_update, report_date, is_overview = false }) {
    const reportURL = new URLSearchParams(window.location.search).get("report_url") ?? window.location.href;
    const title = is_overview ? "About these reports" : "About this report";
    if (report_date === null) {
        report_date = new Date();
    }
    const listItems = [
        <List.Item key={"reportURL"} data-testid={"reportUrl"}>
            <List.Content verticalAlign={"middle"}>
                <ExportCardItem url={reportURL}>{report.title}</ExportCardItem>
            </List.Content>
        </List.Item>,
        <List.Item key={"date"}>
            <List.Content verticalAlign={"middle"}>
                <ExportCardItem>{"Report date: " + formatDate(report_date)}</ExportCardItem>
            </List.Content>
        </List.Item>,
        <List.Item key={"generated"}>
            <List.Content verticalAlign={"middle"}>
                <ExportCardItem>{"Generated: " + formatDate(last_update) + ", " + formatTime(last_update)}</ExportCardItem>
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
    report: reportPropType,
    last_update: datePropType,
    report_date: datePropType,
    is_overview: bool,
}

function formatDate(date) {
    return date.toLocaleDateString('en-GB', { year: 'numeric', month: '2-digit', day: '2-digit'}).replace(/\//g, '-');
}

function formatTime(date) {
    return date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit'});
}