import { useContext } from "react";
import { DarkMode } from "../context/DarkMode";
import { MetricDetails } from '../metric/MetricDetails';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import './SubjectTableRow.css';

export function SubjectTableRow(
    {
        changed_fields,
        children,
        first_metric,
        last_metric,
        metric_uuid,
        metric,
        report,
        reportDate,
        reports,
        subject_uuid,
        visibleDetailsTabs,
        toggleVisibleDetailsTab,
        nrDates,
        reload,
        stopSorting
    }
) {
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
            stopSorting={stopSorting}
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

    const darkMode = useContext(DarkMode)
    const style = nrDates > 1 ? { background: darkMode ? "rgba(60, 60, 60, 1)" : "#f9fafb" } : {}
    const className = nrDates === 1 ? metric.status || "unknown" : ""
    return (
        <TableRowWithDetails id={metric_uuid} className={className} details={details} style={style} expanded={expanded} onExpand={(state) => onExpand(state)}>
            {children}
        </TableRowWithDetails>
    )
}
