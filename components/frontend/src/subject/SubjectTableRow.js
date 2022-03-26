import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import './SubjectTableRow.css';

export function SubjectTableRow(
    {
        children,
        details,
        metric_uuid,
        metric,
        visibleDetailsTabs,
        toggleVisibleDetailsTab,
        nrDates,
        style,
    }
) {
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

    const className = nrDates === 1 ? metric.status || "unknown" : ""
    return (
        <TableRowWithDetails id={metric_uuid} className={className} details={details} style={style} expanded={expanded} onExpand={(state) => onExpand(state)}>
            {children}
        </TableRowWithDetails>
    )
}
