import React from 'react';
import { Dropdown, Table } from 'semantic-ui-react';
import { format_metric_direction, get_metric_direction } from '../utils';
import "./TrendTable.css";

function HamburgerHeader() {
    return (
        <Dropdown item icon='sidebar'>
            <Dropdown.Menu>
                <Dropdown.Header>Interval length</Dropdown.Header>
                <Dropdown.Item>1 week</Dropdown.Item>
                <Dropdown.Item>2 weeks</Dropdown.Item>
                <Dropdown.Item>3 weeks</Dropdown.Item>
                <Dropdown.Item>4 weeks</Dropdown.Item>
                <Dropdown.Header>Number of periods</Dropdown.Header>
                <Dropdown.Item>3</Dropdown.Item>
                <Dropdown.Item>4</Dropdown.Item>
                <Dropdown.Item>5</Dropdown.Item>
                <Dropdown.Item>6</Dropdown.Item>
                <Dropdown.Item>7</Dropdown.Item>
            </Dropdown.Menu>
        </Dropdown>
    )
}

function Header({ dates }) {
    const cells = [];
    for (const date of dates) {
        cells.push(<Table.HeaderCell key={date} textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>);
    }
    return (
        <Table.Header>
            <Table.Row>
                <Table.HeaderCell style={{ background: "#f9fafb", pointerEvents: "revert", fontWeight: "revert", color: "revert", boxShadow: "revert" }}>
                    <HamburgerHeader />
                </Table.HeaderCell>
                {cells}
            </Table.Row>
        </Table.Header>
    )
}

function Body({ values, unit }) {
    const measurements = [];
    const targets = [];
    values.forEach(([value, status, target, direction], date) => {
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

export function TrendTable({ data_model, measurements, metric, report_date, scale, unit }) {
    const base_date = report_date ? new Date(report_date) : new Date();
    const direction = get_metric_direction(metric, data_model);
    const target = metric.target || "0";
    let values = new Map();
    [0, 7, 14, 21, 28, 35, 42, 49].forEach((offset) => {
        let date = new Date(base_date.getTime());
        date.setDate(date.getDate() - offset);
        values.set(date, offset === 0 && !report_date ? [metric.value || "?", metric.status, target, direction] : ["?", "unknown", "?", "≤"]);
    });
    measurements.forEach((measurement) => {
        values.forEach((value, date) => {
            if (value[0] !== "?") { return }
            const iso_date = date.toISOString();
            if (measurement.start <= iso_date && iso_date <= measurement.end) {
                values.set(date, [measurement[scale].value, measurement[scale].status, measurement[scale].target, format_metric_direction(measurement[scale].direction)])
            }
        })
    });
    return (
        <Table definition size='small'>
            <Header dates={values.keys()} />
            <Body values={values} unit={unit} />
        </Table>
    )
}