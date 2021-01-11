import React from 'react';
import { Dropdown, Table } from 'semantic-ui-react';
import { format_metric_direction, get_metric_direction } from '../utils';
import { HamburgerMenu } from '../widgets/HamburgerMenu';
import "./TrendTable.css";

function HamburgerHeader({ setTrendTableInterval, setTrendTableNrDates, trendTableInterval, trendTableNrDates }) {
    return (
        <HamburgerMenu>
            <Dropdown.Header>Number of dates</Dropdown.Header>
            {[2, 3, 4, 5, 6, 7].map((nr) =>
                <Dropdown.Item key={nr} active={nr === trendTableNrDates} onClick={() => setTrendTableNrDates(nr)}>{nr}</Dropdown.Item>
            )}
            <Dropdown.Header>Time between dates</Dropdown.Header>
            {[1, 2, 3, 4].map((nr) =>
                <Dropdown.Item key={nr} active={nr === trendTableInterval} onClick={() => setTrendTableInterval(nr)}>{`${nr} week${nr === 1 ? '' : 's'}`}</Dropdown.Item>
            )}
        </HamburgerMenu>
    )
}

function Header({ dates, setTrendTableInterval, setTrendTableNrDates, trendTableInterval, trendTableNrDates }) {
    const cells = [];
    for (const date of dates) {
        cells.push(<Table.HeaderCell key={date} textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>);
    }
    return (
        <Table.Header>
            <Table.Row>
                <Table.HeaderCell style={{ background: "#f9fafb", pointerEvents: "revert", fontWeight: "revert", color: "revert", boxShadow: "revert" }}>
                    <HamburgerHeader
                        setTrendTableInterval={setTrendTableInterval} setTrendTableNrDates={setTrendTableNrDates}
                        trendTableInterval={trendTableInterval} trendTableNrDates={trendTableNrDates} />
                </Table.HeaderCell>
                {cells}
            </Table.Row>
        </Table.Header>
    )
}

function Body({ table, unit }) {
    const measurements = [];
    const targets = [];
    table.forEach(([value, status, target, direction], date) => {
        measurements.push(<Table.Cell className={status} key={date} textAlign="right">{value}{unit}</Table.Cell>)
        targets.push(<Table.Cell key={date} textAlign="right">{direction} {target}{unit}</Table.Cell>)
    });
    return (
        <Table.Body>
            <Table.Row>
                <Table.Cell>Measurement</Table.Cell>
                {measurements}
            </Table.Row>
            <Table.Row>
                <Table.Cell>Target</Table.Cell>
                {targets}
            </Table.Row>
        </Table.Body>
    )
}

export function TrendTable({ data_model, measurements, metric, report_date, scale, setTrendTableInterval, setTrendTableNrDates, trendTableInterval, trendTableNrDates, unit }) {
    const base_date = report_date ? new Date(report_date) : new Date();
    const direction = get_metric_direction(metric, data_model);
    const metric_value = metric.value === null ? "?" : metric.value;
    const status = metric.status === null ? "unknown" : metric.status;
    const target = metric.target || "0";
    const interval_length = trendTableInterval * 7;  // trendTableInterval is in weeks, convert to days
    let table = new Map();  // Keys are the dates, values are the metric value, status, target and direction per date
    for (let offset = 0; offset < trendTableNrDates * interval_length; offset += interval_length) {
        let date = new Date(base_date.getTime());
        date.setDate(date.getDate() - offset);
        table.set(date, ((offset === 0 && !report_date) ? [metric_value, status, target, direction] : ["?", "unknown", "?", "≤"]));
    }
    measurements.forEach((measurement) => {
        table.forEach((value, date) => {
            if (value[0] !== "?") { return }
            const iso_date = date.toISOString();
            if (measurement.start <= iso_date && iso_date <= measurement.end) {
                const measurement_value = measurement[scale].value === null ? "?" : measurement[scale].value;
                table.set(date, [measurement_value, measurement[scale].status, measurement[scale].target, format_metric_direction(measurement[scale].direction)])
            }
        })
    });

    const targets = [];
    table.forEach(([target, direction], date) => {
        targets.push(<Table.Cell key={date} textAlign="right">{direction} {target}{unit}</Table.Cell>)
    });
    return (
        <Table definition size='small'>
            <Header
                dates={table.keys()} setTrendTableInterval={setTrendTableInterval} setTrendTableNrDates={setTrendTableNrDates}
                trendTableInterval={trendTableInterval} trendTableNrDates={trendTableNrDates} />
            <Body table={table} unit={unit} />
            <Table.Body>
                <Table.Row>
                    <Table.Cell>Measurement</Table.Cell>
                    {measurements}
                </Table.Row>
                <Table.Row>
                    <Table.Cell>Target</Table.Cell>
                    {targets}
                </Table.Row>
            </Table.Body>
        </Table>
    )
}