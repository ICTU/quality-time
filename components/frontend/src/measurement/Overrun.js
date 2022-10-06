import { getMetricResponseOverrun, pluralize } from '../utils';

export function Overrun({ metric_uuid, metric, report, measurements }) {
    const overrun = getMetricResponseOverrun(metric_uuid, metric, report, measurements);
    return (
        overrun > 0 ? `${overrun} ${pluralize("day", overrun)}` : ""
    )
}
