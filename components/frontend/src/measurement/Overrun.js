import { Header, Popup, Table } from '../semantic_ui_react_wrappers';
import { string } from 'prop-types';
import { StatusIcon } from './StatusIcon';
import { getMetricResponseOverrun, pluralize } from '../utils';
import { datesPropType, measurementsPropType, metricPropType, reportPropType } from '../sharedPropTypes';

function formatDays(days) {
    return `${days} ${pluralize("day", days)}`
}

export function Overrun({ metric_uuid, metric, report, measurements, dates }) {
    const { totalOverrun, overruns } = getMetricResponseOverrun(metric_uuid, metric, report, measurements);
    if (totalOverrun === 0) { return null }
    const triggerText = formatDays(totalOverrun)
    let trigger = <span>{triggerText}</span>
    const sortedDates = dates.slice().sort((d1, d2) => d1.getTime() > d2.getTime())
    const period = `${sortedDates.at(0).toLocaleDateString()} - ${sortedDates.at(-1).toLocaleDateString()}`
    const content = (
        <>
        <Header>
            <Header.Content>
                Metric reaction time overruns<Header.Subheader>In the period {period}</Header.Subheader>
            </Header.Content>
        </Header>
        <Table compact size="small">
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell textAlign="center" colSpan="3">When did the metric need action?</Table.HeaderCell>
                    <Table.HeaderCell textAlign="center" colSpan="3">How long did it take to react?</Table.HeaderCell>
                </Table.Row>
                <Table.Row>
                    <Table.HeaderCell textAlign="center">Status</Table.HeaderCell>
                    <Table.HeaderCell textAlign="center">Start</Table.HeaderCell>
                    <Table.HeaderCell textAlign="center">End</Table.HeaderCell>
                    <Table.HeaderCell textAlign="right">Actual</Table.HeaderCell>
                    <Table.HeaderCell textAlign="right">Desired</Table.HeaderCell>
                    <Table.HeaderCell textAlign="right">Overrun</Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {overruns.map((overrun) => (
                    <Table.Row key={overrun.start}>
                        <Table.Cell textAlign="center"><StatusIcon size="small" status={overrun.status}/></Table.Cell>
                        <Table.Cell>{overrun.start.split("T")[0]}</Table.Cell>
                        <Table.Cell>{overrun.end.split("T")[0]}</Table.Cell>
                        <Table.Cell textAlign="right">{formatDays(overrun.actual_response_time)}</Table.Cell>
                        <Table.Cell textAlign="right">{formatDays(overrun.desired_response_time)}</Table.Cell>
                        <Table.Cell textAlign="right">{formatDays(overrun.overrun)}</Table.Cell>
                    </Table.Row>
                ))}
            </Table.Body>
            <Table.Footer>
                <Table.Row>
                    <Table.HeaderCell colSpan="5"><b>Total</b></Table.HeaderCell>
                    <Table.HeaderCell textAlign="right"><b>{triggerText}</b></Table.HeaderCell>
                </Table.Row>
            </Table.Footer>
        </Table>
        </>
    )
    return (
        <Popup
            content={content}
            flowing
            hoverable
            trigger={trigger}
        />
    )
}
Overrun.propTypes = {
    dates: datesPropType,
    measurements: measurementsPropType,
    metric: metricPropType,
    metric_uuid: string,
    report: reportPropType,
}
