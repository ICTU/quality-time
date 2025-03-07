import { Box } from "@mui/material"
import { func, number, string } from "prop-types"
import { useContext } from "react"

import { add_source, copy_source, move_source } from "../api/source"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import {
    measurementPropType,
    measurementSourcePropType,
    metricPropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from "../sharedPropTypes"
import { pluralize } from "../utils"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddDropdownButton } from "../widgets/buttons/AddDropdownButton"
import { CopyButton } from "../widgets/buttons/CopyButton"
import { MoveButton } from "../widgets/buttons/MoveButton"
import { source_options } from "../widgets/menu_options"
import { showMessage } from "../widgets/toast"
import { InfoMessage } from "../widgets/WarningMessage"
import { Source } from "./Source"
import { sourceTypeOptions } from "./SourceType"

function ButtonSegment({ metric, metric_uuid, reload, reports }) {
    const dataModel = useContext(DataModel)
    return (
        <ReadOnlyOrEditable
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            editableComponent={
                <ButtonRow paddingLeft={0} paddingRight={0} paddingTop={2}>
                    <AddDropdownButton
                        itemType="source"
                        itemSubtypes={sourceTypeOptions(dataModel, metric.type)}
                        onClick={(subtype) => add_source(metric_uuid, subtype, reload)}
                    />
                    <CopyButton
                        itemType="source"
                        onChange={(source_uuid) => copy_source(source_uuid, metric_uuid, reload)}
                        get_options={() => source_options(reports, dataModel, metric.type)}
                    />
                    <MoveButton
                        itemType="source"
                        onChange={(source_uuid) => move_source(source_uuid, metric_uuid, reload)}
                        get_options={() => source_options(reports, dataModel, metric.type, metric_uuid)}
                    />
                </ButtonRow>
            }
        />
    )
}
ButtonSegment.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    reports: reportsPropType,
}

function SourceSegment({
    changed_fields,
    index,
    last_index,
    measurement_source,
    metric,
    reload,
    report,
    settings,
    sourceUuid,
}) {
    return (
        <Box id={sourceUuid} sx={{ border: 1, borderColor: "divider", padding: "8px" }}>
            <Source
                first_source={index === 0}
                last_source={index === last_index}
                metric={metric}
                measurement_source={measurement_source}
                reload={reload}
                report={report}
                settings={settings}
                source_uuid={sourceUuid}
                changed_fields={changed_fields}
            />
        </Box>
    )
}
SourceSegment.propTypes = {
    changed_fields: stringsPropType,
    index: number,
    last_index: number,
    measurement_source: measurementSourcePropType,
    metric: metricPropType,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
    sourceUuid: string,
}

export function Sources({ reports, report, metric, metric_uuid, measurement, changed_fields, reload, settings }) {
    const dataModel = useContext(DataModel)
    const measurementSources = measurement?.sources ?? []
    const sourceUuids = Object.keys(metric.sources).filter((sourceUuid) =>
        Object.keys(dataModel.sources).includes(metric.sources[sourceUuid].type),
    )

    const reload_source = (json) => {
        const nr_sources = json.nr_sources_mass_edited
        if (nr_sources > 0) {
            showMessage("info", `Changed ${nr_sources} ${pluralize("source", nr_sources)}`)
        }
        reload(json)
    }

    const lastIndex = sourceUuids.length - 1
    const sourceSegments = sourceUuids.map((sourceUuid, index) => {
        return (
            <SourceSegment
                key={sourceUuid}
                metric={metric}
                report={report}
                sourceUuid={sourceUuid}
                index={index}
                last_index={lastIndex}
                measurement_source={measurementSources.find((source) => source.source_uuid === sourceUuid)}
                changed_fields={changed_fields}
                reload={reload_source}
                settings={settings}
            />
        )
    })
    return (
        <>
            {sourceSegments.length === 0 ? (
                <InfoMessage title="No sources">No sources have been configured yet.</InfoMessage>
            ) : (
                sourceSegments
            )}
            <ButtonSegment reports={reports} metric_uuid={metric_uuid} metric={metric} reload={reload} />
        </>
    )
}
Sources.propTypes = {
    changed_fields: stringsPropType,
    reports: reportsPropType,
    report: reportPropType,
    metric: metricPropType,
    metric_uuid: string,
    measurement: measurementPropType,
    reload: func,
    settings: settingsPropType,
}
