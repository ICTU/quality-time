import { Table } from "semantic-ui-react";
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { MetricDetails } from '../metric/MetricDetails';
import { formatMetricScale, formatMetricUnit, formatMetricScaleAndUnit, format_minutes, get_metric_name } from "../utils";
import './TrendTable.css';

export function MeasurementsRow(
    {
        changed_fields,
        datamodel,
        first_metric,
        last_metric,
        metric_uuid,
        metricType,
        metricName,
        metric,
        measurements,
        dates,
        report,
        reportDate,
        reports_overview,
        subject_uuid,
        visibleDetailsTabs,
        toggleVisibleDetailsTab,
        reload
    }
) {
    const unit = formatMetricUnit(metricType, metric)
    const measurementCells = []
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    measurements.sort((m1, m2) => m1.start < m2.start ? 1 : -1)

    dates.forEach((date) => {
        const iso_date_string = date.toISOString().split("T")[0];
        const measurement = measurements?.find((m) => { return m.start.split("T")[0] <= iso_date_string && iso_date_string <= m.end.split("T")[0] })
        let metric_value = !measurement?.[metric.scale]?.value ? "?" : measurement[metric.scale].value;
        metric_value = metric_value !== "?" && metricType.unit === "minutes" && metric.scale !== "percentage" ? format_minutes(metric_value) : metric_value;
        const status = !measurement?.[metric.scale]?.status ? "unknown" : measurement[metric.scale].status;
        measurementCells.push(<Table.Cell className={status} key={date} textAlign="right">{metric_value}{formatMetricScale(metric)}</Table.Cell>)
    })

    const metric_type = datamodel.metrics[metric.type];
    const latest_measurements = metric.recent_measurements;
    const latest_measurement = latest_measurements?.length > 0 ? latest_measurements[latest_measurements.length - 1] : null;
    const metric_unit = formatMetricScaleAndUnit(metric_type, metric);
    const metric_name = get_metric_name(metric, datamodel);
    const details = (
        <MetricDetails
            first_metric={first_metric}
            last_metric={last_metric}
            measurement={latest_measurement}
            metric_name={metric_name}
            scale={metric.scale}
            unit={formatMetricScaleAndUnit(metric_type, metric, false)}
            datamodel={datamodel}
            report_date={reportDate}
            reports={reports_overview}
            report={report}
            subject_uuid={subject_uuid}
            metric_uuid={metric_uuid}
            metric_unit={metric_unit}
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

    const style = { background: "#f9fafb" }
    return (
        <TableRowWithDetails style={style} details={details} expanded={expanded} onExpand={(state) => onExpand(state)}>
            <Table.Cell style={style}>{metricName}</Table.Cell>
            {measurementCells}
            <Table.Cell style={style}>{unit}</Table.Cell>
        </TableRowWithDetails>
    )
}