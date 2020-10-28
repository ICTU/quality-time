import React from 'react';
import { Table } from 'semantic-ui-react';
import "./TrendTable.css";

function Header({ dates }) {
    const cells = [];
    for (const date of dates) {
        cells.push(<Table.HeaderCell key={date}>{date.toLocaleDateString()}</Table.HeaderCell> );
    }
    return (
        <Table.Header>
            <Table.Row>
                {cells}
            </Table.Row>
        </Table.Header>
    )
}

function Body({ values, unit }) {
    const cells = [];
    values.forEach(([value, status], date) => { cells.push(<Table.Cell className={status} key={date}>{value}{unit}</Table.Cell>) });
    return (
        <Table.Body>
            <Table.Row>
                {cells}
            </Table.Row>
        </Table.Body>
    )
}

export function TrendTable({ measurements, metric, report_date, scale, unit }) {
    const base_date = report_date ? new Date(report_date) : new Date();
    let values = new Map();
    [0, 7, 14, 21, 28, 35, 42, 49].forEach((offset) => {
        let date = new Date(base_date.getTime());
        date.setDate(date.getDate() - offset);
        values.set(date, offset === 0 && !report_date ? [metric.value, metric.status] : ["?", "unknown"]);
    });
    measurements.forEach((measurement) => {
        values.forEach((value, date) => {
            if (value[0] !== "?") { return }
            const iso_date = date.toISOString();
            if (measurement.start <= iso_date && iso_date <= measurement.end) {
                values.set(date, [measurement[scale].value, measurement[scale].status])
            }
        })
    });
    return (
        <Table size='small'>
            <Header dates={values.keys()} />
            <Body values={values} unit={unit} />
        </Table>
    )
}