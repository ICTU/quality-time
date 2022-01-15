import { useContext } from "react";
import { Popup, Table } from "semantic-ui-react";
import { DataModel } from "../context/DataModel";
import { MetricDetails } from '../metric/MetricDetails';
import { IssueStatus } from '../metric/IssueStatus';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { Tag } from '../widgets/Tag';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import { MeasurementSources } from '../metric/MeasurementSources';
import { StatusIcon } from '../metric/StatusIcon';
import { TrendSparkline } from '../metric/TrendSparkline';
import { formatMetricScale, formatMetricScaleAndUnit, format_minutes, formatMetricDirection, get_metric_name, get_metric_tags, get_metric_target, get_metric_value, getMetricUnit } from '../utils';
import './SubjectTableRow.css';

function MeasurementValue({ metric }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metricUnit = formatMetricScaleAndUnit(metricType, metric);
    const metricValue = get_metric_value(metric)
    const value = metricValue && metricType.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metricValue) : metricValue || "?";
    const valueText = <span>{value + metricUnit}</span>
    if (metric.latest_measurement) {
        return (
            <Popup trigger={valueText} flowing hoverable>
                <TimeAgoWithDate date={metric.latest_measurement.end}>{metric.status ? "Metric was last measured":"Last measurement attempt"}</TimeAgoWithDate><br />
                <TimeAgoWithDate date={metric.latest_measurement.start}>{metric.status ? "Value was first measured":"Value unknown since"}</TimeAgoWithDate>
            </Popup>
        )
    }
    return valueText;
}

function MeasurementTarget({ metric }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metricUnit = formatMetricScaleAndUnit(metricType, metric);
    const metric_direction = formatMetricDirection(metric, dataModel)
    let debt_end = "";
    if (metric.debt_end_date) {
        const end_date = new Date(metric.debt_end_date);
        debt_end = ` until ${end_date.toLocaleDateString()}`;
    }
    const debt = metric.accept_debt ? ` (debt accepted${debt_end})` : "";
    let target = get_metric_target(metric);
    if (target && metricType.unit === "minutes" && metric.scale !== "percentage") {
        target = format_minutes(target)
    }
    return `${metric_direction} ${target}${metricUnit}${debt}`
}

export function SubjectTableRow(
    {
        changed_fields,
        first_metric,
        last_metric,
        metric_uuid,
        metric,
        measurements,
        dates,
        report,
        reportDate,
        reports,
        subject_uuid,
        hiddenColumns,
        visibleDetailsTabs,
        toggleVisibleDetailsTab,
        trendTableNrDates,
        reload
    }
) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const unit = getMetricUnit(metric, dataModel)
    const measurementCells = []
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    measurements.sort((m1, m2) => m1.start < m2.start ? 1 : -1)

    dates.forEach((date) => {
        const iso_date_string = date.toISOString().split("T")[0];
        const measurement = measurements?.find((m) => { return m.start.split("T")[0] <= iso_date_string && iso_date_string <= m.end.split("T")[0] })
        let metric_value = measurement?.[metric.scale]?.value ?? "?";
        metric_value = metric_value !== "?" && metricType.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metric_value) : metric_value;
        const status = measurement?.[metric.scale]?.status ?? "unknown";
        measurementCells.push(<Table.Cell className={status} key={date} textAlign="right">{metric_value}{formatMetricScale(metric)}</Table.Cell>)
    })

    const metricName = get_metric_name(metric, dataModel);
    const details = (
        <MetricDetails
            first_metric={first_metric}
            last_metric={last_metric}
            report_date={reportDate}
            reports={reports}
            report={report}
            subject_uuid={subject_uuid}
            metric_uuid={metric_uuid}
            changed_fields={changed_fields}
            visibleDetailsTabs={visibleDetailsTabs}
            toggleVisibleDetailsTab={toggleVisibleDetailsTab}
            stop_sort={() => {/* Dummy implementation */ }}
            reload={reload} />
    )

    const expanded = visibleDetailsTabs.filter((tab) => tab?.startsWith(metric_uuid)).length > 0;
    function onExpand(expand) {
        if (expand) {
            toggleVisibleDetailsTab(`${metric_uuid}:0`)
        } else {
            const tabs = visibleDetailsTabs.filter((each) => each?.startsWith(metric_uuid));
            if (tabs.length > 0) {
                toggleVisibleDetailsTab(tabs[0])
            }
        }
    }

    const style = trendTableNrDates > 1 ? { background: "#f9fafb" } : {}
    const className = trendTableNrDates === 1 ? metric.status : ""
    return (
        <TableRowWithDetails id={metric_uuid} className={className} details={details} expanded={expanded} onExpand={(state) => onExpand(state)}>
            <Table.Cell style={style}>{metricName}</Table.Cell>
            {trendTableNrDates > 1 && measurementCells}
            {trendTableNrDates > 1 && <Table.Cell style={style}>{unit}</Table.Cell>}
            {trendTableNrDates === 1 && !hiddenColumns.includes("trend") && <Table.Cell><TrendSparkline measurements={metric.recent_measurements} report_date={reportDate} scale={metric.scale} /></Table.Cell>}
            {trendTableNrDates === 1 && !hiddenColumns.includes("status") && <Table.Cell textAlign='center'><StatusIcon status={metric.status} status_start={metric.status_start} /></Table.Cell>}
            {trendTableNrDates === 1 && !hiddenColumns.includes("measurement") && <Table.Cell><MeasurementValue metric={metric} /></Table.Cell>}
            {trendTableNrDates === 1 && !hiddenColumns.includes("target") && <Table.Cell><MeasurementTarget metric={metric} /></Table.Cell>}
            {!hiddenColumns.includes("source") && <Table.Cell style={style}><MeasurementSources metric={metric} /></Table.Cell>}
            {!hiddenColumns.includes("comment") && <Table.Cell style={style}><div dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>}
            {!hiddenColumns.includes("issues") && <Table.Cell style={style}><IssueStatus metric={metric} issueTracker={report.issue_tracker} /></Table.Cell>}
            {!hiddenColumns.includes("tags") && <Table.Cell style={style}>{get_metric_tags(metric).map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>}
        </TableRowWithDetails>
    )
}