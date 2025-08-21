import { array } from "prop-types"

import { settingsPropType, sourcePropType } from "../sharedPropTypes"
import { entityStatusEndDate, entityStatusRationale } from "./source_entity_status"

export function determineColumnsToHide(settings, source, sourceEntities) {
    if (!settings.hideEmptyColumns.value) {
        return []
    }
    const emptyColumns = []
    if (sourceEntities.every((entity) => entityStatusRationale(source, entity) === "")) {
        emptyColumns.push("rationale")
    }
    if (sourceEntities.every((entity) => entityStatusEndDate(source, entity) === "")) {
        emptyColumns.push("status_end_date")
    }
    return emptyColumns
}
determineColumnsToHide.propTypes = {
    settings: settingsPropType,
    source: sourcePropType,
    sourceEntries: array,
}
