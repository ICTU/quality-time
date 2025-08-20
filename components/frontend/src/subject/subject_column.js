import { array, number } from "prop-types"

import { dataModelPropType, measurementsPropType, reportPropType, settingsPropType } from "../sharedPropTypes"
import {
    getMetricComment,
    getMetricIssueIds,
    getMetricResponseOverrun,
    getMetricResponseTimeLeft,
    getMetricTags,
} from "../utils"

export function determineColumnsToHide(dataModel, measurements, metricEntries, nrDates, report, settings) {
    // First, add columns that are hidden explicitly by the user:
    const columnsToHide = new Set(settings.hiddenColumns.value)
    // Next, if the user wants to hide empty columns, add any empty columns:
    if (settings.hideEmptyColumns.value) {
        if (metricEntries.every(([_, metric]) => getMetricComment(metric) === "")) {
            columnsToHide.add("comment")
        }
        if (metricEntries.every(([_, metric]) => getMetricIssueIds(metric).length === 0)) {
            columnsToHide.add("issues")
        }
        if (metricEntries.every(([_, metric]) => getMetricTags(metric).length === 0)) {
            columnsToHide.add("tags")
        }
        if (metricEntries.every(([_, metric]) => getMetricResponseTimeLeft(metric, report) === null)) {
            columnsToHide.add("time_left")
        }
        if (
            metricEntries.every(
                ([metricUuid, metric]) =>
                    getMetricResponseOverrun(metricUuid, metric, report, measurements, dataModel).overruns.length === 0,
            )
        ) {
            columnsToHide.add("overrun")
        }
    }
    // Finally, hide columns depending on how many dates are being shown:
    if (nrDates <= 1) {
        columnsToHide.add("overrun")
    } else {
        columnsToHide.add("trend")
        columnsToHide.add("status")
        columnsToHide.add("measurement")
        columnsToHide.add("target")
    }
    return Array.from(columnsToHide).toSorted()
}
determineColumnsToHide.propTypes = {
    dataModel: dataModelPropType,
    measurements: measurementsPropType,
    metricEntries: array,
    nrDates: number,
    report: reportPropType,
    settings: settingsPropType,
}
